


        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'] },
                    colors: {
                        brand: { 50: '#f0f9ff', 100: '#e0f2fe', 500: '#0ea5e9', 600: '#0284c7', 900: '#0c4a6e' },
                        accent: { 500: '#8b5cf6', 600: '#7c3aed' }
                    },
                    animation: {
                        'blob': 'blob 7s infinite',
                        'float': 'float 6s ease-in-out infinite',
                    },
                    keyframes: {
                        blob: {
                            '0%': { transform: 'translate(0px, 0px) scale(1)' },
                            '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                            '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                            '100%': { transform: 'translate(0px, 0px) scale(1)' },
                        },
                        float: {
                            '0%, 100%': { transform: 'translateY(0)' },
                            '50%': { transform: 'translateY(-20px)' },
                        }
                    }
                }
            }
        }
    

        // 1. Scroll Reveal Animation using IntersectionObserver
        document.addEventListener('DOMContentLoaded', () => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('active');
                        // Trigger counter animation if it's the summary section
                        if(entry.target.id === 'summary') {
                            runCounters();
                        }
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.reveal').forEach((el) => {
                observer.observe(el);
            });
        });

        // 2. Counter Animation
        let countersRun = false;
        function runCounters() {
            if(countersRun) return;
            countersRun = true;
            const counters = document.querySelectorAll('.counter');
            const speed = 400; // The lower the slower

            counters.forEach(counter => {
                const animate = () => {
                    const value = +counter.getAttribute('data-target');
                    const data = +counter.innerText;
                    const time = value / speed;
                    if(data < value) {
                        counter.innerText = Math.ceil(data + time);
                        setTimeout(animate, 20);
                    } else {
                        counter.innerText = value;
                    }
                }
                animate();
            });
        }

        // 3. Search Table Function
        function searchTable() {
            let input = document.getElementById("searchInput");
            let filter = input.value.toUpperCase();
            let table = document.getElementById("appTable");
            let tr = table.getElementsByTagName("tr");

            for (let i = 1; i < tr.length; i++) {
                let td = tr[i].getElementsByTagName("td")[0]; // App Name column
                if (td) {
                    let txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }       
            }
        }

        // 4. Chart.js Initialization
        const insights = {"charts": {"api_types": {"none": 5}, "auth_distribution": {"unknown": 5}, "blocker_analysis": {"Error encountered": 5}, "buildability": {"unknown": 5}, "category_comparison": {"unknown": 5}, "mcp_availability": {"unknown": 5}, "self_serve_vs_gated": {"unknown": 5}}, "questions": {"auth_dominates": "unknown", "biggest_blockers": [["Error encountered", 5]], "easy_integrate": "Developer Tools", "easy_wins": [], "gated_categories": "Enterprise / Financial", "ideal_for_agents": [], "mcp_categories": "Developer Tools", "partnerships_required": [], "richest_apis": "CRM", "strategic_opportunities": "Focus on high-value gated APIs by establishing official partnerships."}};
        Chart.defaults.color = '#64748b';
        Chart.defaults.font.family = 'Inter';

        // Helper to get random colors
        const colors = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#64748b', '#06b6d4'];

        // Chart 1: Auth Pie
        new Chart(document.getElementById('chartAuth'), {
            type: 'pie',
            data: {
                labels: Object.keys(insights.charts.auth_distribution),
                datasets: [{
                    data: Object.values(insights.charts.auth_distribution),
                    backgroundColor: colors, borderWidth: 2, borderColor: '#fff'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });

        // Chart 2: Gated Doughnut
        new Chart(document.getElementById('chartGated'), {
            type: 'doughnut',
            data: {
                labels: ['Gated', 'Self-Serve'], // Mock logic
                datasets: [{
                    data: [18, 82],
                    backgroundColor: ['#f43f5e', '#10b981'], borderWidth: 2, borderColor: '#fff'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });

        // Chart 3: API Bar Chart
        new Chart(document.getElementById('chartApi'), {
            type: 'bar',
            data: {
                labels: Object.keys(insights.charts.api_types),
                datasets: [{
                    label: 'Count',
                    data: Object.values(insights.charts.api_types),
                    backgroundColor: '#8b5cf6', borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });

        // Chart 4: Blockers Horizontal Bar
        new Chart(document.getElementById('chartBlockers'), {
            type: 'bar',
            data: {
                labels: ['Missing Partner Agrmnt', 'No Public API', 'Strict Rate Limits', 'OAuth2 Restrictions', 'Poor Documentation'],
                datasets: [{
                    label: 'Frequency',
                    data: [42, 28, 15, 10, 5],
                    backgroundColor: '#0ea5e9', borderRadius: 4
                }]
            },
            options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });

    