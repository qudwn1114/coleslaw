const btn_submit = document.getElementById("btn-submit");
const person_type_id = document.getElementById("person_type_id");
const description = document.getElementById("description");

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
    person_type_id.disabled=true;
    description.disabled=true;
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
            customAlert(data.message, ()=>{
                location.href=data.url;
            });
        },
        error: function(error) {
            btn_submit.disabled=false;
            person_type_id.disabled=false;
            description.disabled=false;
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
    if(person_type_id.value == ''){
        person_type_id.focus();
        return false;
    }
    return true;
}