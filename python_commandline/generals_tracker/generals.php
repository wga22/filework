<?php
declare(strict_types=1);
date_default_timezone_set('America/New_York');

function escapeHtml(?string $value): string
{
    return htmlspecialchars($value ?? '', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function formatMinutes(float $minutes): string
{
    return number_format($minutes / 60, 2) . ' h';
}

function formatSessionDuration(float $minutes): string
{
    $totalMinutes = (int) floor(max(0, $minutes));
    $hours = intdiv($totalMinutes, 60);
    $remainingMinutes = $totalMinutes % 60;

    return $hours > 0
        ? sprintf('%dh %dm', $hours, $remainingMinutes)
        : sprintf('%dm', $remainingMinutes);
}

$databaseSettings = [
    'host' => getenv('CHAMFOX_DB_HOST'),
    'port' => getenv('CHAMFOX_DB_PORT'),
    'dbname' => getenv('CHAMFOX_DB_NAME'),
    'user' => getenv('CHAMFOX_DB_USER'),
    'password' => getenv('CHAMFOX_DB_PASS'),
];

foreach ($databaseSettings as $setting) {
    if ($setting === false || $setting === '') {
        http_response_code(500);
        exit('Database configuration is incomplete.');
    }
}

$users = [];
$dailyPeriods = [];
$monthlyPeriods = [];
$errorMessage = null;

try {
    $connection = new PDO(
        sprintf(
            'pgsql:host=%s;port=%s;dbname=%s',
            $databaseSettings['host'],
            $databaseSettings['port'],
            $databaseSettings['dbname']
        ),
        $databaseSettings['user'],
        $databaseSettings['password'],
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]
    );

    $userQuery = $connection->query(
        "SELECT
            u.user_name,
            MAX(u.last_seen) AS last_seen,
            COALESCE(BOOL_OR(s.row_id IS NOT NULL AND s.end_time IS NULL), FALSE) AS currently_online,
            COALESCE(
                MAX(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - s.start_time)) / 60.0)
                    FILTER (WHERE s.row_id IS NOT NULL AND s.end_time IS NULL),
                0
            ) AS current_session_minutes
        FROM tesla.users AS u
        LEFT JOIN tesla.sessions AS s ON s.user_row_id = u.row_id
        GROUP BY u.user_name
        ORDER BY u.user_name"
    );

    foreach ($userQuery as $row) {
        $users[$row['user_name']] = [
            'last_seen' => $row['last_seen'],
            'currently_online' => filter_var($row['currently_online'], FILTER_VALIDATE_BOOLEAN),
            'current_session_minutes' => (float) $row['current_session_minutes'],
            'last_24_hours' => 0.0,
            'daily' => [],
            'average_total' => 0.0,
            'monthly' => [],
        ];
    }

    $last24HoursQuery = $connection->query(
        "SELECT
            u.user_name,
            SUM(
                s.duration_mins
                * EXTRACT(EPOCH FROM (
                    LEAST(COALESCE(s.end_time, CURRENT_TIMESTAMP), CURRENT_TIMESTAMP)
                    - GREATEST(s.start_time, CURRENT_TIMESTAMP - INTERVAL '24 hours')
                ))
                / NULLIF(EXTRACT(EPOCH FROM (
                    COALESCE(s.end_time, CURRENT_TIMESTAMP) - s.start_time
                )), 0)
            ) AS minutes
        FROM tesla.sessions AS s
        JOIN tesla.users AS u ON u.row_id = s.user_row_id
        WHERE s.start_time < CURRENT_TIMESTAMP
            AND COALESCE(s.end_time, CURRENT_TIMESTAMP) > CURRENT_TIMESTAMP - INTERVAL '24 hours'
        GROUP BY u.user_name"
    );

    foreach ($last24HoursQuery as $row) {
        if (isset($users[$row['user_name']])) {
            $users[$row['user_name']]['last_24_hours'] = (float) $row['minutes'];
        }
    }

    $playtimeQuery = $connection->query(
        "WITH periods AS (
            SELECT
                'day'::text AS period_type,
                day_start AS period_start,
                day_start + INTERVAL '1 day' AS period_end
            FROM generate_series(
                CURRENT_DATE::timestamp - INTERVAL '6 days',
                CURRENT_DATE::timestamp,
                INTERVAL '1 day'
            ) AS day_start
            UNION ALL
            SELECT
                'average'::text AS period_type,
                day_start AS period_start,
                day_start + INTERVAL '1 day' AS period_end
            FROM generate_series(
                CURRENT_DATE::timestamp - INTERVAL '59 days',
                CURRENT_DATE::timestamp,
                INTERVAL '1 day'
            ) AS day_start
            UNION ALL
            SELECT
                'month'::text AS period_type,
                month_start AS period_start,
                month_start + INTERVAL '1 month' AS period_end
            FROM generate_series(
                date_trunc('month', CURRENT_DATE)::timestamp - INTERVAL '11 months',
                date_trunc('month', CURRENT_DATE)::timestamp,
                INTERVAL '1 month'
            ) AS month_start
        ),
        session_data AS (
            SELECT
                u.user_name,
                s.start_time,
                COALESCE(s.end_time, CURRENT_TIMESTAMP) AS effective_end,
                s.duration_mins
            FROM tesla.sessions AS s
            JOIN tesla.users AS u ON u.row_id = s.user_row_id
        ),
        allocations AS (
            SELECT
                sd.user_name,
                p.period_type,
                p.period_start,
                SUM(
                    sd.duration_mins
                    * EXTRACT(EPOCH FROM (
                        LEAST(sd.effective_end, p.period_end AT TIME ZONE current_setting('TimeZone'))
                        - GREATEST(sd.start_time, p.period_start AT TIME ZONE current_setting('TimeZone'))
                    ))
                    / NULLIF(EXTRACT(EPOCH FROM (sd.effective_end - sd.start_time)), 0)
                ) AS minutes
            FROM session_data AS sd
            JOIN periods AS p
                ON sd.start_time < p.period_end AT TIME ZONE current_setting('TimeZone')
                AND sd.effective_end > p.period_start AT TIME ZONE current_setting('TimeZone')
            GROUP BY sd.user_name, p.period_type, p.period_start
        )
        SELECT user_name, period_type, period_start::date AS period_start, minutes
        FROM allocations
        ORDER BY period_type, period_start, user_name"
    );

    foreach ($playtimeQuery as $row) {
        $periodDate = $row['period_start'];
        if ($row['period_type'] === 'day') {
            $dailyPeriods[$periodDate] = $periodDate;
            if (isset($users[$row['user_name']])) {
                $users[$row['user_name']]['daily'][$periodDate] = (float) $row['minutes'];
            }
        } elseif ($row['period_type'] === 'average') {
            if (isset($users[$row['user_name']])) {
                $users[$row['user_name']]['average_total'] += (float) $row['minutes'];
            }
        } else {
            $monthlyPeriods[$periodDate] = $periodDate;
            if (isset($users[$row['user_name']])) {
                $users[$row['user_name']]['monthly'][$periodDate] = (float) $row['minutes'];
            }
        }
    }

    $periodQuery = $connection->query(
        "SELECT period_type, period_start::date AS period_start
        FROM (
            SELECT 'day'::text AS period_type, day_start AS period_start
            FROM generate_series(
                CURRENT_DATE::timestamp - INTERVAL '6 days',
                CURRENT_DATE::timestamp,
                INTERVAL '1 day'
            ) AS day_start
            UNION ALL
            SELECT 'month'::text AS period_type, month_start AS period_start
            FROM generate_series(
                date_trunc('month', CURRENT_DATE)::timestamp - INTERVAL '11 months',
                date_trunc('month', CURRENT_DATE)::timestamp,
                INTERVAL '1 month'
            ) AS month_start
        ) AS all_periods
        ORDER BY period_type, period_start"
    );

    foreach ($periodQuery as $row) {
        if ($row['period_type'] === 'day') {
            $dailyPeriods[$row['period_start']] = $row['period_start'];
        } else {
            $monthlyPeriods[$row['period_start']] = $row['period_start'];
        }
    }
    ksort($dailyPeriods);
    ksort($monthlyPeriods);
} catch (Throwable $exception) {
    error_log('Generals tracker dashboard error: ' . $exception->getMessage());
    http_response_code(500);
    $errorMessage = 'Unable to load player statistics. Check the database connection and schema.';
}

$anyOnline = false;
foreach ($users as $user) {
    $anyOnline = $anyOnline || $user['currently_online'];
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><defs><linearGradient id='bg' x1='0%25' y1='0%25' x2='100%25' y2='100%25'><stop offset='0%25' stop-color='%232b2d26'/><stop offset='100%25' stop-color='%23141512'/></linearGradient><linearGradient id='gold' x1='0%25' y1='0%25' x2='0%25' y2='100%25'><stop offset='0%25' stop-color='%23f5c542'/><stop offset='50%25' stop-color='%23d49b1a'/><stop offset='100%25' stop-color='%238c6208'/></linearGradient></defs><polygon points='18,4 46,4 60,18 60,46 46,60 18,60 4,46 4,18' fill='url(%23bg)' stroke='url(%23gold)' stroke-width='4'/><circle cx='32' cy='32' r='20' fill='none' stroke='%234a4d3f' stroke-width='1.5' stroke-dasharray='6 4'/><path d='M 24 11 L 32 7 L 40 11' fill='none' stroke='%232d7dd2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/><path d='M 11 42 L 13 50 L 21 52' fill='none' stroke='%23d9381e' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/><path d='M 53 42 L 51 50 L 43 52' fill='none' stroke='%234c9a2a' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/><polygon points='32,16 36.2,26.8 47.8,27.5 38.8,34.8 41.8,46 32,39.6 22.2,46 25.2,34.8 16.2,27.5 27.8,26.8' fill='url(%23gold)' stroke='%23141512' stroke-width='1' stroke-linejoin='round'/></svg>">
    <title>Generals Player Activity</title>
    <style>
        :root {
            color-scheme: light;
            font-family: "Segoe UI", Tahoma, sans-serif;
            color: #202a26;
            background: #f0f2ef;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            background: #f0f2ef;
            transition: background-color 180ms ease;
        }

        body.online { background: #e8f4e9; }

        main {
            width: min(100% - 32px, 1440px);
            margin: 0 auto;
            padding: 32px 0 56px;
        }

        header {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 20px;
            padding-bottom: 22px;
            border-bottom: 1px solid #bdc8c0;
        }

        h1, h2, p { margin: 0; }
        h1 { font-size: 1.8rem; font-weight: 650; }
        h2 { margin: 30px 0 12px; font-size: 1.15rem; }
        .subtitle { margin-top: 6px; color: #56635b; }

        .status {
            display: inline-flex;
            align-items: center;
            gap: 9px;
            font-weight: 650;
            white-space: nowrap;
        }

        .status::before {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #707b75;
            content: "";
        }

        .online .status::before { background: #278443; }
        .table-wrap { overflow-x: auto; border: 1px solid #cbd3cd; background: rgba(255, 255, 255, .72); }
        table { width: 100%; border-collapse: collapse; font-size: .92rem; }
        th, td { padding: 10px 12px; border-bottom: 1px solid #dce2dd; text-align: right; white-space: nowrap; }
        th { background: rgba(222, 230, 224, .72); color: #34443a; font-weight: 650; }
        th:first-child, td:first-child { position: sticky; left: 0; text-align: left; }
        th:first-child { background: #e0e7e1; }
        td:first-child { background: #f8faf8; font-weight: 600; }
        tr:last-child td { border-bottom: 0; }
        .online-label { color: #236d37; font-weight: 650; }
        .muted { color: #68756d; }
        .error { margin-top: 24px; padding: 14px 16px; border-left: 4px solid #a34a3b; background: #fff3ef; }
        @media (max-width: 640px) {
            main { width: min(100% - 20px, 1440px); padding-top: 22px; }
            header { align-items: start; flex-direction: column; }
            h1 { font-size: 1.5rem; }
            th, td { padding: 9px; }
        }
    </style>
</head>
<body class="<?= $anyOnline ? 'online' : '' ?>">
<main>
    <header>
        <div>
            <h1>Generals Player Activity</h1>
            <p class="subtitle">Last seen and recorded playtime by player</p>
        </div>
        <p class="status"><?= $anyOnline ? 'Players currently online' : 'No players currently online' ?></p>
    </header>

    <?php if ($errorMessage !== null): ?>
        <p class="error"><?= escapeHtml($errorMessage) ?></p>
    <?php else: ?>
        <section aria-labelledby="players-heading">
            <h2 id="players-heading">Players</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th scope="col">Player</th>
                        <th scope="col">Status</th>
                        <th scope="col">Last seen online</th>
                        <th scope="col">Last 24 hours</th>
                        <th scope="col">60-day daily average</th>
                    </tr>
                    </thead>
                    <tbody>
                    <?php if ($users === []): ?>
                        <tr><td colspan="5" class="muted">No tracked players found.</td></tr>
                    <?php else: ?>
                        <?php foreach ($users as $name => $user): ?>
                            <?php
                            $dailyAverage = $user['average_total'] / 60;
                            ?>
                            <tr>
                                <td><?= escapeHtml($name) ?></td>
                                <td class="<?= $user['currently_online'] ? 'online-label' : 'muted' ?>">
                                    <?= $user['currently_online'] ? 'Online' : 'Offline' ?>
                                </td>
                                <td>
                                    <?php if ($user['last_seen'] !== null): ?>
                                        <time datetime="<?= escapeHtml($user['last_seen']) ?>"><?= escapeHtml(date('M j, Y H:i', strtotime($user['last_seen']))) ?></time>
                                    <?php else: ?>
                                        <span class="muted">Never</span>
                                    <?php endif; ?>
                                    <?php if ($user['currently_online']): ?>
                                        <br><span class="muted">Current session: <?= escapeHtml(formatSessionDuration($user['current_session_minutes'])) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td><?= escapeHtml(formatMinutes($user['last_24_hours'])) ?></td>
                                <td><?= escapeHtml(formatMinutes($dailyAverage)) ?></td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </section>

        <section aria-labelledby="daily-heading">
            <h2 id="daily-heading">Playtime per day <span class="muted">(last 7 days)</span></h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th scope="col">Player</th>
                        <?php foreach ($dailyPeriods as $period): ?>
                            <th scope="col"><?= escapeHtml(date('D M j', strtotime($period))) ?></th>
                        <?php endforeach; ?>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($users as $name => $user): ?>
                        <tr>
                            <td><?= escapeHtml($name) ?></td>
                            <?php foreach ($dailyPeriods as $period): ?>
                                <td><?= escapeHtml(formatMinutes($user['daily'][$period] ?? 0.0)) ?></td>
                            <?php endforeach; ?>
                        </tr>
                    <?php endforeach; ?>
                    <?php if ($users === []): ?>
                        <tr><td colspan="8" class="muted">No tracked players found.</td></tr>
                    <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </section>

        <section aria-labelledby="monthly-heading">
            <h2 id="monthly-heading">Playtime per month <span class="muted">(last 12 months)</span></h2>
            <div class="table-wrap">
                <table>
                    <thead>
                    <tr>
                        <th scope="col">Player</th>
                        <?php foreach ($monthlyPeriods as $period): ?>
                            <th scope="col"><?= escapeHtml(date('M Y', strtotime($period))) ?></th>
                        <?php endforeach; ?>
                    </tr>
                    </thead>
                    <tbody>
                    <?php foreach ($users as $name => $user): ?>
                        <tr>
                            <td><?= escapeHtml($name) ?></td>
                            <?php foreach ($monthlyPeriods as $period): ?>
                                <td><?= escapeHtml(formatMinutes($user['monthly'][$period] ?? 0.0)) ?></td>
                            <?php endforeach; ?>
                        </tr>
                    <?php endforeach; ?>
                    <?php if ($users === []): ?>
                        <tr><td colspan="13" class="muted">No tracked players found.</td></tr>
                    <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </section>
    <?php endif; ?>
</main>
</body>
</html>