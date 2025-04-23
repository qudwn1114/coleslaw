const btn_submit = document.getElementById("btn-submit");
const table_name = document.getElementById("table_name");
const count = document.getElementById("count");

btn_submit.addEventListener("click", () => {
    if(!validation()){
        return;
    }
    customConfirm("등록 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        const data =new FormData(document.getElementById("data-form"));
    btn_submit.disabled=true;
    table_name.disabled=true;
    count.disabled=true;
    $.ajax({
        type: "POST",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: data,
        enctype: "multipart/form-data", //form data 설정
        processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
        contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
        success: function(data) {
            customAlert(data.message);
            location.href=data.url;
        },
        error: function(error) {
            btn_submit.disabled=false;
            table_name.disabled=false;
            count.disabled=false;
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
    });
})

//유효성 체크 함수
function validation(){
    if(table_name.value == ''){
        table_name.focus();
        return false;
    }
    if(count.value <= 0){
        count.focus();
        return false;
    }
    return true;
}