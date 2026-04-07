@extends('layouts.app')

@section('title', 'Home')

@section('content')
    <section class="home-hero" id="home">
        <div class="site-container home-hero-content">
            <h1>
                Khám phá <span class="text-gradient">Đà Nẵng</span>
            </h1>
            <p>
                Thành phố đáng sống nhất Việt Nam - Nơi biển xanh hòa quyện với núi non hùng vĩ
            </p>

            <form action="{{ route('destinations.index') }}" method="GET" class="hero-search" role="search">
                <div class="hero-search-field">
                    <svg class="hero-search-icon" viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm10 2-4.35-4.35" fill="none" stroke="currentColor"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <input type="text" name="search" placeholder="Tìm điểm đến, hoạt động, ẩm thực...">
                </div>
                <button type="submit" class="btn-primary">Tìm kiếm</button>
            </form>

            <div class="hero-quick-links">
                <a href="{{ route('destinations.index') }}" class="btn-ghost">Xem tất cả điểm đến</a>
                <a href="{{ route('destinations.index', ['rating' => 4.5]) }}" class="btn-ghost">Top đánh giá</a>
            </div>
        </div>
        <span class="hero-scroll" aria-hidden="true"></span>
    </section>

    @if ($homeError)
        <section class="section-pad">
            <div class="site-container">
                <div class="alert alert-error" role="alert">
                    <strong>Không thể tải đầy đủ dữ liệu trang chủ.</strong>
                    <p>{{ $homeError }} Bạn vẫn có thể tiếp tục khám phá danh sách điểm đến.</p>
                    <a href="{{ route('destinations.index') }}" class="btn-secondary">Mở danh sách điểm đến</a>
                </div>
            </div>
        </section>
    @endif

    <section class="section-pad section-soft-cyan" id="destinations">
        <div class="site-container">
            <div class="section-heading">
                <h2>Điểm đến <span class="text-gradient">nổi bật</span></h2>
                <p>
                    Khám phá những địa danh du lịch nổi tiếng và hấp dẫn nhất tại Đà Nẵng
                </p>
            </div>

            <div class="destination-grid">
                @forelse ($featured as $destination)
                    @include('components.destination-card', ['destination' => $destination])
                @empty
                    @if (!$homeError)
                        <div class="card-skeleton-grid" aria-hidden="true">
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                        </div>
                    @endif

                    <div class="empty-state">
                        <p>Chưa có địa điểm nổi bật.</p>
                    </div>
                @endforelse
            </div>

            @component('components.destination-detail-modal')
            @endcomponent
        </div>
    </section>

    <section class="section-pad" id="activities">
        <div class="site-container">
            <div class="section-heading">
                <h2>Hoạt động <span class="text-gradient">du lịch</span></h2>
                <p>Đa dạng các hoạt động thú vị cho mọi lứa tuổi và sở thích</p>
            </div>

            <div class="category-grid">
                @php
                    $activities = [
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAABxUlEQVR4nO3YPWtUURDG8U3QwohFYqOVTbJsQhoDFvkAqS20EhJjpSAq+AVM5Uud0tIileBaScq8EVALjRG01k2qjVaWP7kwxSJ6dw13g27mD6c5d2bOzGW4Z+5TqyVJMnhgBNfRxC7a+IxV3MNYie9Y2KyGTztiNCPmSD8TP4MH+K6cH3iGOZyLNRd7xbMyithLxVm1ipMfx1dHRwv1Kgu4/csBn/AQl3AWE9ECGz0ktxG29WipKdyNVurkfpUFnMfrOGQBwyW2k3iELezF2oyCGyV+wxH7I3ZwobICkiRJkn8CnMQVPMUb7Mc3/zmu4VQPM9iL8NmLGCu4jBP9TvxWD+PIAZYxi9FYs7H3rYvvF9zsSyHY7jjoHe7gYgx607iB9R7GkLWwnQ7fmRhD3nfYbPWjgPUYQ4r2GeoyhjyJ1mjHeht7kyV+Q7gaY8ha5QUkSZJUB07HjfgyPo0HoTC8istq9BCqRBFrsYhdYaq/VSWW/mdVomWAVIndGAemYl6pH0KVmAjfI1UlPmC+iyrRCAViM95k6y9UifkoJFWJJEmSAUQ1qkQz7qP9+N1MVaIrx0mVaODxH1SJRolfqhJJMoj8BBF1IfgQKUc1AAAAAElFTkSuQmCC" alt="sea-waves">',
                            'title' => 'Lướt sóng & Thể thao nước',
                            'description' =>
                                'Trải nghiệm các hoạt động thể thao nước như lướt sóng, lặn biển, và jet ski',
                            'gradient' => 'blue',
                        ],
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAAC9klEQVR4nO2YTUgVURTHr6ZYUUkLy6APNxFREEIfRFFBIEFErcpd0JNWtgixrYEQRbXIVeQmApGCoja5CnETERVkQR+LCrLvyMgk7cNfHPs/uo1vnk+b95iB+YE4c+995/zPzL3n3LnOpaSkpKTkAChzSQfYCTS6JANUAo+Bp0CFSypAC3854JIIsAAY9AJ5AVS5pAGcUwDXgfu6bnZJAqgHfgKjwApgtwJ5Dcx2SQHok/CTXtsttbW6JAA0SvA7oNprb1D7R2CeizPALC1qI5Ojv1d9bS7OAEcl9B5QnqN/k/qHgBoXR4DFwFdgDNiSZ1yPgjnu4gjQLYHdgfYam3Le/VoFOwzUujgBbPbELfHaVwLPlLEWeu2XFXSHiwtAOXBXwt4Aq9S+PVDZn3t9GbWNAEtdHACaJMreiPEZOAF81709/ZshfUZnHIKoVr0w9gOXPIHjC1pvzNLyxUBfJ/BDf8tLKXqbbQQDbaclqk/3ZcAxPfGmwNgJfQrG6CpVEBXAE+BBNhjtoUa1p6oPjA+d936fXWud/AJWFzmMcYcHvSnxCFikXa1x9j9td8jOlegU53Zk8/ult38yBvR/MDjdpmG/Vml7zGpMdMonOmqV6Dv6WOr33s7hiHxYJjN6orAXlpVst2o0eJW6X1OsMiI/872aszUKm0EH7TLeG2i3YDZG7KvNz4BRGjaxX2Q8UtEh/uYA7/23H5XhbDa5GpnRyX0ekc/b2UM9YAOwa7oG67z8viZqwZNkyAEFY9/5VcBD1bCpr0fggoydL4ri/L4PybcV31NehpzaCYxVWO8EpK5oisP9V3mfy/5m9IN/BlCIoWv64ZmiKs6vIRPYeN7IXhdqYL2ewJD/IVRqgBk6M7ZaNVPnZLZevwHLCjGQPeVoL4ni/Fr2Wsby7rsK2ikDOzTwk1VaF8/DjWHNmHVhg8q8z9UWF1P4s17Cqz+wTwNexflsFpgLvJXWPbkWli0qgl91cQRoltbpFcmUlJSUlBT3L78Bc9m5Rw430MoAAAAASUVORK5CYII=" alt="mountain">',
                            'title' => 'Leo núi & Trekking',
                            'description' => 'Chinh phục các đỉnh núi và khám phá thiên nhiên hoang sơ',
                            'gradient' => 'green',
                        ],
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAACmUlEQVR4nO2ay4tOcRjHX9M0mozLYihEIytkQy5J1GymJGuxZa1szITYYSH/AOWyETs2IooxUdiIkNtOlMS4lFw+et7zPTrO/M687zm/3zFMv8/q/Z3f83yf59uc2/u80wCuMXEMN3IA14E7pY8zwTgaq3a8KKBuWjaWIxqpm2gkRzQSimgkRzQSimgkRzQSimjkPzIyDNwocfzfNFKWSWnkkz5PC9NiW8V7VPNjSCMv9XlRmDbbKr5YNZ976syQzqgtbmmxIVyrLRvYqJojnjr90rlni2Na7A/XassGDqjmUU+di797BzZrMebWVhfATdXc5KExJI03wKz0wnsP/ASWhW3Z2cBy1XpX9gZD0mt/5i/xxdbZgCPaOFlH87lmzqjWoZJ5I/zJM2BdPmi+3H0fsxkQYL1qfAbmlsxNOQtsB7qKAndnnPaEaj6jP91ut6qxq0J+k3YCO+yCT8K5AnRXbdqh3Q1clbaNODtqM2IAvcBD5VyyB07DE2AmcFmapt1bUadJmQS7Xp4kac1TYU2VwtJaC7yQ1mNgnodWkyrn8/kklR/AOWBJifylwGngmzQuNO/1HiCqJE4BdgKvMoZuA3uBPkd8H7BPMRaLcneYlo8JLyMp9tACBnVqpLx2xNkTNuURsCfkGzW+RnJiK4sEMyZWBClWp5HxBIMXyhGNFBGNeEI0UkA04gnRyGQ2QvIyaXxw7I3WOegjsJHV0rvv2HugvVVBitVs5JT0Djv2ah1gEMII0AkclJadQgscMQttlqsYi+30KhrCCDAVmKOpx1DmFd6+KG0dJ2+bpiQoZ1Aas03zrxoh+UHFxVNgoI38AU1i2vr/rLqNfAXeAneB48CWwjmSW6NLOSekYVqmWXksW/SLVcov/clFE5QqPL8AAAAASUVORK5CYII=" alt="food">',
                            'title' => 'Tour ẩm thực',
                            'description' => 'Thưởng thức đặc sản địa phương và khám phá văn hóa ẩm thực',
                            'gradient' => 'orange',
                        ],
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAACsklEQVR4nO2YPU8UURSGxwYhbsyudlgZC/AvCEosBTsTCxuyEUhsTXSxlKjon9Bf4EdiJeBH7NQfgKuFCQELG5BFEyx8zMF3kmGYYefO7O7MJvMkm0zuzjlz3nvuuV+eV1JSUpIE4AjQAL7jzjdg1isCwE2ycy1vEaeBX8Bf4GqKTPqd8AM42b1I2wfzUoE8SWlvYpbk43EnA7sMvAZ2HIZFpt4EziirSWkpxqk4h/dw5zdwJUvn6ds3gD8pvr8QlQljF7gNDHsFBRjWLGmxGpPBP9+oseH1CfwXY6wEG7fVuC8TwADwSGvEBrBobV5xMmP8DDbuEfHyQw7ywCsIhOM+RIhlwTgHjOl5o43zGlAHXgCfNQPu6Pm5/qvlJWQMGNfzeozTIeAOsEV7NoF5YLBXQhYjgrgfM14/Bd55BcwAI8Ax/UbV5i+AxscsMyQOQgYkxjKzbiLCxS4Ra3Jhw2c8QQDngaZs1tKKIamQBI6GApl4C1QdbK2W3sn2Q5phRgeFWE0Yqy4iQmKaadcwOiFEQfiF3XY4HeJnIjAB1PIQUvcL28UuxteyfE3nIcTWBOO6i12Mr1n5epqHEH9sj7jYxfga9Wc9Lwchdi4wKi52Mb4q8tXqdyHHD2wAE1AOrZhin/EyAszlWex1mS252MX4Wslz+q1pETMuuNiG/FyUD/NV7bmQ0BalmeaMoc74Ih+3Uth3TMigtuJoA5hYDHACeF+ITWPENt56d8JLNpy+FmYbHxJjveqzrJnorBa7ip7nAoXtZ6L7B6sUw6wRmAAOY1P3Z0czfnOP+IZszqs2jQLPdE5p6beqtuk0Z5couiqklxAhJPKCrsgApxTzVrDRbrf77cp0PurKdEqNuyrYfrrEvhR+YYH+426c2knN837NFJFtxbg/EyUlJSUlXg78A9skggdbjWIsAAAAAElFTkSuQmCC" alt="camera--v3">',
                            'title' => 'Chụp ảnh & Sightseeing',
                            'description' => 'Săn những góc ảnh đẹp tại các địa danh nổi tiếng',
                            'gradient' => 'purple',
                        ],
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAACzUlEQVR4nO2ZO2hUQRiFb0J8NBZqY2OMFj5Qu+AjakBiI6JoYSwsBRERQRQEEXwUQTRGRNAmlZYWWhhEEUSDYhArUXF1NUFU8FEEC8Uin/zyb7iue+fO3Duzu4F7YGGL8585Z+4/s3dmoygwUERTHRRBmgxFkHoDuEt+DDdDEC+Y8q1DEcQziiCNCgI8CrFY676bYcbDHLrDISaoaVqAIohHYaAFWAWcBd4Db/V7Z4jxnGAjDCwHTgIlQ9uPAReB9RI4z3iZkCQcM/+myvBozHBSwNGkUNQjiMF86mxbBm8JEgRorTIbxzvX/ldNMbsaOF9Ds+QtiJqX2TkDlLP0ueN4lSdVtm2/NMH5wAXgYw3Bc7obeTFvmMB1ar7ag+x+p4E5aSJLgW9VM9+vLRDMfEqoDcAl4FPMlzy1eabCG0p8AKxphPmUUBuBZ+px0LT4vispOW2DASxRjx9MpB9KWmgpugv4CvTmMOakAXRWdjYT6bqSBixFXyn/pYP3XBrAVeX3m0iyI6FPZq6F6C/l/3T0n0kDaAd+66c9jXxPhU85zOYLR/+ZNIAB5V6zEe5Rsiz8WSncXuALsNPRv7MGMFs7ZQJYaSv+WMMcjpoEwHH1dMulaLsWfQZmBnVo52eGehF0uxTKb8pzLdwb1KWdn33qZSRL8W4tfh3EXbYNYUeW4rbKi00Qd25eKmjNJeDdWb19UATxC4ogiiKIZ1AEUUzu3nAUmB4ZoBcGN4EjnrndMR9taWfhZcAiORnqIIeA+/x/i9IHbAYWAwv0XL9fX/0nPHLXAgdqeBhT7lZgBdABbAO6JMgxkiG3FQeB2wZO3FAIblk7YsjAGZcgm4CnWiADPAEu6wxNPko5A8hhS/9XL8W4V4AtwDSP3JEED3KJdwK4E+PKjc+eyKKXhwL0vX8u/66RkH0fgtthu0ZC9b1v7njSGgnR96G4f9fIH3aVTN94uWbpAAAAAElFTkSuQmCC" alt="water-transportation">',
                            'title' => 'Du thuyền & Câu cá',
                            'description' => 'Trải nghiệm du thuyền trên biển và câu cá ngoài khơi',
                            'gradient' => 'indigo',
                        ],
                        [
                            'icon' =>
                                '<img width="30px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAAC5UlEQVR4nO2abWiNYRjH7zljVhbZpqZoSsoHWvJhS/kkJPngrdBQat7KJ18opWWLkmhWQiYlHw8pRZE172XZh3lJXrLyMkNeIq8/3e3/5HZsp+ds5+Hcj/P7dHZd99V13TvPfd//57qPMXny/HuARuA98AS4DOwHxhrfALr5kwdAufEJIKni9wE1QKv+Pg8kjC8As1X4I2AIMAbokm2n8QWgALivwufJZr+Zz8APYKHxBWCzJnLasW2U7R0w2fgAUAp8Ar4DExx7iyZzDxhpfAA4rqIbHVsxcFP2U/YxNLkOMFMFvwSGO/aJwBv5thofADpV8PIU+wIt/G/AHJPrAJs0kbY+fA3y9QCVf6ugI0r6CtiVQdwo4INip6T4EsA5+ey6KY6keBfnmcY9H8IAHFJMcx++MuCx/C0maoDrSnbS+Q+G2nGAaYp5C5T04Z+urdqyLpIJBABNwS7jyI3FJiTA1XSFAmvkt6d/tYkKYLUSnQDq9PkuUBgyfqViOtKMOagxT4GKrE4gAJjqyPGEJmGpNSEAihx5X5NmzA2NuQQMNdkGKAQ+au+38mMZA+dYmjzjdYAOlm7gIrAeGJaapE2D5kqedwwwiV3YZWkmMwv4SvbotGrCTbBbjm0mx6F3W18K3HbejUYHziWp0jzXAUYA7ap7T2AcJ8Nz4xFAlep+ERgqZHhm/JxIj6tYfX60mgPjDhm2mxwHKNeaDha71XOlgfOsjPO93X7p7Yy8lqPCkwOxFdjw24EITNKALkmUO4OQKNUhJMqFsDouI4AVSpB0lGomonGVYm6FeG+JVDTuVZJ64KE+L8og/ppi6vrx18r/BZiR1eJdgCtKdGYAL1ZVTmOupB+/FaSWtSZKiNGr7mHnqz/gbfMhNu2g/7pBx6+WqT0/ivppmW4xHjWxG1Ka2O1Oa6nAp2uFSsd+1KtrBeJw0UNcrt6I0WVoMi7X093E5AcD9Tongp9wNEUmy/PkMTnBT8/JzcPBD37RAAAAAElFTkSuQmCC" alt="airplane-mode-on--v1">',
                            'title' => 'Tour kết hợp',
                            'description' => 'Các tour du lịch kết hợp nhiều điểm đến và hoạt động',
                            'gradient' => 'cyan',
                        ],
                    ];
                @endphp
                @forelse ($activities as $activitie)
                    <article class="activity-card">
                        <span class="activity-icon {{ $activitie['gradient'] }}">{!! $activitie['icon'] !!}</span>
                        <h3 class="activity-title">{{ $activitie['title'] }}</h3>
                        <p class="muted activity-desc">
                            {{ $activitie['description'] ?? 'Khám phá những trải nghiệm phù hợp với bạn.' }}</p>
                        {{-- <a href="{{ route('destinations.index', ['activitie_slug' => $activitie['slug']]) }}"
                            class="btn-secondary activity-link">Tìm hiểu thêm <span aria-hidden="true">→</span></a> --}}
                    </article>
                @empty
                    @if (!$homeError)
                        <div class="card-skeleton-grid" aria-hidden="true">
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                        </div>
                    @endif

                    <div class="empty-state">
                        <p>Chưa có dữ liệu hoạt động.</p>
                    </div>
                @endforelse
            </div>
        </div>
    </section>

    <section class="section-pad section-soft-cyan" id="cuisine">
        <div class="site-container">
            <div class="section-heading">
                <h2>Ẩm thực <span class="text-gradient">Đà Nẵng</span></h2>
                <p>Khám phá hương vị đặc trưng của ẩm thực miền Trung Việt Nam</p>
            </div>

            @php
                $dishes = [
                    [
                        'name' => 'Mì Quảng',
                        'price' => '30.000 - 50.000đ',
                        'desc' => 'Món mì truyền thống đặc trưng của miền Trung với nước dùng đậm đà.',
                    ],
                    [
                        'name' => 'Bún chả cá',
                        'price' => '35.000 - 60.000đ',
                        'desc' => 'Bún tươi kết hợp với chả cá thơm ngon, đặc sản Đà Nẵng.',
                    ],
                    [
                        'name' => 'Bánh tráng cuốn thịt heo',
                        'price' => '40.000 - 70.000đ',
                        'desc' => 'Món ăn nhẹ nhàng, thanh mát với bánh tráng mỏng và thịt heo luộc.',
                    ],
                    [
                        'name' => 'Bê thui Cầu Mống',
                        'price' => '150.000 - 300.000đ',
                        'desc' => 'Thịt bê non thui thơm phức, món đặc sản nổi tiếng.',
                    ],
                    [
                        'name' => 'Hải sản tươi sống',
                        'price' => 'Theo thời giá',
                        'desc' => 'Hải sản tươi ngon được chế biến theo nhiều cách.',
                    ],
                    [
                        'name' => 'Bánh xèo',
                        'price' => '25.000 - 45.000đ',
                        'desc' => 'Bánh xèo giòn tan với nhân tôm, thịt, giá đỗ.',
                    ],
                ];
            @endphp

            <div class="cuisine-layout">
                <article class="cuisine-hero">
                    <img src="https://images.unsplash.com/photo-1696654351863-4d9a6d9cd4b9?auto=format&fit=crop&w=1200&q=80"
                        alt="Am thuc da nang">
                    <div class="cuisine-highlight">
                        <span class="cuisine-highlight-badge" aria-hidden="true">
                            <svg viewBox="0 0 24 24">
                                <path d="M7 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                                <path d="M5 10h14v7a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-7Z" fill="none" stroke="currentColor"
                                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                <path d="M9 15h6" fill="none" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </span>
                        <div>
                            <p class="cuisine-stat-label">Hơn</p>
                            <p class="cuisine-stat-value">1000+ món ăn</p>
                        </div>
                    </div>
                </article>

                <div class="cuisine-list">
                    @foreach ($dishes as $dish)
                        <article class="cuisine-card">
                            <div class="cuisine-card-top">
                                <h3 class="cuisine-dish-title">{{ $dish['name'] }}</h3>
                                <span class="cuisine-price">{{ $dish['price'] }}</span>
                            </div>
                            <p class="muted cuisine-dish-desc">{{ $dish['desc'] }}</p>
                        </article>
                    @endforeach
                </div>
            </div>
        </div>
    </section>
@endsection
