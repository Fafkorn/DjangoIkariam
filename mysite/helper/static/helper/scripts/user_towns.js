var users = [{% for user_name in compare_user_names %} '{{user_name}}', {% endfor %}];


            function numberWithSpaces(x) {
                return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
            }

            function removeUser(username) {
                users = users.filter(e => e !== username);
                console.log(username);
                console.log(users);

                var usersForm = document.getElementById("users-div");
                console.log(usersForm);

                while (usersForm.hasChildNodes()) {
                    usersForm.removeChild(usersForm.lastChild);
                }

                for(var i=0; i < users.length; i++) {
                    var input = document.createElement("input");
                    input.type = "hidden";
                    input.name = "compare_user";
                    input.value = users[i];
                    usersForm.appendChild(input);

                    var p = document.createElement("div");
                    p.onclick = function() { removeUser(users[i]); };
                    p.innerHTML = users[i];
                    usersForm.appendChild(p);
                }
            }

            var colors = [
                "rgba(255, 255, 255, 1)",
                "rgba(81, 205, 160, 1)",
                "rgba(223, 121, 112, 1)",
                "rgba(76, 156, 160, 1)",
                "rgba(174, 125, 153, 1)",
                "rgba(201, 212, 92, 1)"
            ];
            var backgroundColors = [
                "rgba(255, 255, 255, 0.05)",
                "rgba(81, 205, 160, 0.05)",
                "rgba(223, 121, 112, 0.05)",
                "rgba(76, 156, 160, 0.05)",
                "rgba(174, 125, 153, 0.05)",
                "rgba(201, 212, 92, 0.05)"
            ];


            window.onload = function script() {

            removeUser('');
            var all_islands = {{all_islands}};
                var myTable = document.getElementById('islandTable');
                for (var i = 0; i < all_islands.length; i++) {
                    myTable.rows[all_islands[i][1]].cells[all_islands[i][0]].title  = '[' + all_islands[i][0] + ':' + all_islands[i][1] + ']';
                    myTable.rows[all_islands[i][1]].cells[all_islands[i][0]].style.background  = '#444';
                }
            var occupied_islands = {{occupied_islands}};
                var myTable = document.getElementById('islandTable');
                for (var i = 0; i < occupied_islands.length; i++) {
                    myTable.rows[occupied_islands[i][1]].cells[occupied_islands[i][0]].title  = '[' + occupied_islands[i][0] + ':' + occupied_islands[i][1] + ']';
                    myTable.rows[occupied_islands[i][1]].cells[occupied_islands[i][0]].style.background  = '#666';
                }
            var searched_islands = {{searched_islands}};
                for (var i = 0; i < searched_islands.length; i++) {
                    var myTable = document.getElementById('islandTable');
                    myTable.rows[searched_islands[i][1]].cells[searched_islands[i][0]].style.background  = '#0f0';

                }
            var own_islands = {{own_islands}};
            for (var i = 0; i < own_islands.length; i++) {
                var myTable = document.getElementById('islandTable');
                myTable.rows[own_islands[i][1]].cells[own_islands[i][0]].style.background  = '#fff';

            }

            var config = {
                  type: 'line',
                  data: {
                    datasets: [{
                      data: [{% for data in chart_data %} { x: new Date({{data.0.year}}, {{data.0.month}}-1, {{data.0.day}}), y: {{data.1}} }, {% endfor %}],
                      label: '{{user.user_name}}' + ' + (' + numberWithSpaces({{user_points_income}}) + ')',
                      labels: [{% for data in chart_data %} {{data.1}}, {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[0],
                      backgroundColor: backgroundColors[0],
                      borderColor: colors[0]
                    },
                    {% for compare_data in compare_datas %}
                    {
                      data: [{% for data in compare_data.data %} { x: new Date({{data.0.year}}, {{data.0.month}}-1, {{data.0.day}}), y: {{data.1}} }, {% endfor %}],
                      label: '{{compare_data.username}}' + ' + (' + numberWithSpaces({{compare_data.difference}}) + ')',
                      labels: [{% for data in compare_data.data %} {{data.1}}, {% endfor %}],
                      lineTension: 0.3,
                      pointRadius: 3,
                      pointBorderColor: colors[{{forloop.counter}} % colors.length],
                      backgroundColor: backgroundColors[{{forloop.counter}} % backgroundColors.length],
                      borderColor: colors[{{forloop.counter}} % colors.length]
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
                                return numberWithSpaces(dataset.labels[index]);
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
            var ctx = document.getElementById('chart').getContext('2d');
            window.chart = new Chart(ctx, config);
            };