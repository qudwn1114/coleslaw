report('WEEK');
function report(report_type){
      $.ajax({
          type: "GET",
          url: `/shop-manage/${shop_id}/main/report/?report_type=${report_type}`,
          headers: {
              'X-CSRFToken': csrftoken
          },
          success: function(data) {
            document.getElementById("report_title_en").innerText = data.title_en;
            chart.updateOptions({
                series:[
                    {
                        name: '현장',
                        data: data.pos_data
                    },
                    {
                        name: '온라인',
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
                  alert('로그인 해주세요.');
              }
              else if(error.status == 403){
                  alert('권한이 없습니다!');
              }
              else{
                  alert(error.status + JSON.stringify(error.responseJSON));
              }
          },
    });
}

var options = {
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
        text: '순매출',
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
                    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") + '원'; // 천단위 콤마
                }
                else {
                    return val.toFixed(0).toString() + '원';
                }
           }
        }
    }
}
var chart = new ApexCharts(
    document.querySelector("#salesChart"),
    options
);

chart.render();