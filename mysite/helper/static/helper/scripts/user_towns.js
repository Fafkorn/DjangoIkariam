       var colors = [
            "rgba(255, 255, 255, 1)",
            "rgba(119, 119, 119, 1)",
            "rgba(50, 200, 50, 1)",
            "rgba(200, 50, 50, 1)",
        ];
        var backgroundColors = [
            "rgba(255, 255, 255, 0.05)",
            "rgba(119, 119, 119, 0.05)",
            "rgba(50, 200, 50, 0.05)",
            "rgba(200, 50, 50, 0.05)",
        ];


        window.onload = function script() {
            var users_config = {
                type: 'line',
                data: {
                    datasets: [
                    {
                      data: [{% for data in user_statistics_histories %}
                        {% if data.active_users %}
                            { x: new Date({{data.time.year}}, {{data.time.month}}-1, {{data.time.day}}), y: {{data.active_users}} },
                        {% endif %}
                      {% endfor %}],
                      label: 'Aktywni',
                      labels: [{% for data in user_statistics_histories %} {% if data.active_users %} {{data.active_users}}, {% endif %} {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[0],
                      backgroundColor: backgroundColors[0],
                      borderColor: colors[0]
                    },
                    {
                      data: [{% for data in user_statistics_histories %}
                        {% if data.inactive_users %}
                            { x: new Date({{data.time.year}}, {{data.time.month}}-1, {{data.time.day}}), y: {{data.inactive_users}} },
                        {% endif %}
                      {% endfor %}],
                      label: 'Nieaktywni',
                      labels: [{% for data in user_statistics_histories %} {% if data.inactive_users %} {{data.inactive_users}}, {% endif %} {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[1],
                      backgroundColor: backgroundColors[1],
                      borderColor: colors[1]
                    },
                    {
                      data: [{% for data in user_statistics_histories %}
                        {% if data.on_vacation_users %}
                            { x: new Date({{data.time.year}}, {{data.time.month}}-1, {{data.time.day}}), y: {{data.on_vacation_users}} },
                        {% endif %}
                      {% endfor %}],
                      label: 'Na urlopie',
                      labels: [{% for data in user_statistics_histories %} {% if data.on_vacation_users %} {{data.on_vacation_users}}, {% endif %} {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[2],
                      backgroundColor: backgroundColors[2],
                      borderColor: colors[2]
                    },
                    {
                      data: [{% for data in user_statistics_histories %}
                        {% if data.deleted_users %}
                            { x: new Date({{data.time.year}}, {{data.time.month}}-1, {{data.time.day}}), y: {{data.deleted_users}} },
                        {% endif %}
                      {% endfor %}],
                      label: 'Usunięci',
                      labels: [{% for data in user_statistics_histories %} {% if data.deleted_users %} {{data.deleted_users}}, {% endif %} {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[3],
                      backgroundColor: backgroundColors[3],
                      borderColor: colors[3]
                    },
                    ],
                  },
                  options: {
                    responsive: true,
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                var dataset = data.datasets[tooltipItem.datasetIndex];
                                var index = tooltipItem.index;
                                return dataset.labels[index];
                            }
                        }
                    },
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Chart.js Line Chart'
                      }
                    },
                  scales: {
                    xAxes: [{
                      type: 'time',
                      autoSkip: false
                    }],
                    yAxes: {
                      type: 'number',
                      autoSkip: false
                    },
                  }

                  },
             };
            var ctx = document.getElementById('users_chart').getContext('2d');
            window.users_chart = new Chart(ctx, users_config);

            var alliances_config = {
                type: 'line',
                data: {
                    datasets:
                    [
                        {% for alliance in alliance_histories %}
                        {
                            data: [{% for data in alliance %} { x: new Date({{data.time.year}}, {{data.time.month}}-1, {{data.time.day}}), y: {{data.points}} }, {% endfor %}],
                            label: 'a'{{alliance.0.tag}},
                            labels: [{% for data in alliance %} {{data.points}}, {% endfor %}],
                            lineTension: 0.3,
                            pointRadius: 3,
                            pointBorderColor: colors[0],
                            backgroundColor: backgroundColors[0],
                            borderColor: colors[0]
                        },
                        {% endfor %}
                    ],
                  },
                  options: {
                    responsive: true,
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                var dataset = data.datasets[tooltipItem.datasetIndex];
                                var index = tooltipItem.index;
                                return dataset.labels[index];
                            }
                        }
                    },
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Chart.js Line Chart'
                      }
                    },
                  scales: {
                    xAxes: [{
                      type: 'time',
                      autoSkip: false
                    }],
                    yAxes: {
                      type: 'number',
                      autoSkip: false
                    },
                  }

                  },
             };
            var ctx = document.getElementById('alliances_chart').getContext('2d');
             window.alliances_chart = new Chart(ctx, alliances_config);
        };