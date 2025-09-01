report('WEEK');
shop_report('TODAY');
function report(report_type){
      $.ajax({
          type: "GET",
          url: `/agency-manage/${agency_id}/main/report/?report_type=${report_type}`,
          headers: {
              'X-CSRFToken': csrftoken
          },
          success: function(data) {
            console.log(data);
            document.getElementById("report_title_en").innerText = data.title_en;
            chart1.updateOptions({
                series:[
                    {
                        name: i18n.offline,
                        data: data.pos_data
                    },
                    {
                        name: i18n.online,
                        data: data.online_data
                    },
                ],
                xaxis: {
                    categories: data.categories
                }
            })
          },
          error: function(error) {
              if(error.status == 401){
                  customAlert(i18n.login_required);
              }
              else if(error.status == 403){
                  customAlert(i18n.no_permission);
              }
              else{
                  customAlert(error.status + JSON.stringify(error.responseJSON));
              }
          },
    });
}

var options1 = {
    chart: {
        height: 350,
        type: 'area',
    },
    zoom: {
        enabled: false
    },
    dataLabels: {
        enabled: false
    },
    stroke: {
        curve: 'smooth'
    },
    series: [],
    title: {
        text: i18n.net,
        align: 'left'
    },
    noData: {
      text: 'Loading...'
    },
    grid: {
        row: {
            colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
            opacity: 0.5
        },
    },
    yaxis: {
        labels: {
          formatter: function(val) {
                // override the val here
                if (parseInt(val) >= 1000) {
                    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + i18n.currency; // 천단위 콤마
                }
                else {
                    return val.toFixed(0).toString() + i18n.currency;
                }
           }
        }
    }
}
var chart1 = new ApexCharts(
    document.querySelector("#salesChart"),
    options1
);

chart1.render();

// 가맹점별
function shop_report(report_type){
    $.ajax({
        type: "GET",
        url: `/agency-manage/${agency_id}/main/shop/report/?report_type=${report_type}`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            document.getElementById("shop_report_title_en").innerText = data.title_en;
            chart2.updateOptions({
                series:[
                    {
                        name: i18n.offline,
                        data: data.pos_data
                    },
                    {
                        name: i18n.online,
                        data: data.online_data
                    }
                ],
                xaxis: {
                    categories: data.categories
                }
            });
        },
        error: function(error) {
            if(error.status == 401){
                customAlert(i18n.login_required);
            }
            else if(error.status == 403){
                customAlert(i18n.no_permission);
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
  });
}

var options2 = {
  chart: {
      height: 350,
      type: 'bar',
      stacked: true,
  },
  zoom: {
      enabled: false
  },
  dataLabels: {
    formatter: (val) => {
        return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + i18n.currency;
      }
  },
  plotOptions: {
    bar: {
      borderRadius: 4,
      borderRadiusApplication: 'end',
      horizontal: true,
    }
  },
  series: [],
  title: {
      text: i18n.shop_net,
      align: 'left'
  },
  noData: {
    text: 'Loading...'
  },
  xaxis: {
      labels: {
        formatter: function(val) {
              // override the val here
              if (parseInt(val) >= 1000) {
                  return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + i18n.currency; // 천단위 콤마
              }
              else {
                  return val.toFixed(0).toString() + i18n.currency;
              }
         }
      }
  }, 
  tooltip : {
    enabled : true, 
    y : {
        show : true, 
        formatter : function(val) {
            if (parseInt(val) >= 1000) {
                return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")+ i18n.currency;; // 천단위 콤마
            } else {
                return val.toFixed(0).toString()+ i18n.currency;;
            }
        }
    }
}
}
var chart2 = new ApexCharts(
  document.querySelector("#shopSalesChart"),
  options2
);

chart2.render();