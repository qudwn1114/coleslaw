const btn_submit = document.getElementById("btn-submit");
const btn_address = document.getElementById("btn-address")
const membername = document.getElementById("membername");
const username = document.getElementById("username");
const phone = document.getElementById("phone");
const birth = document.getElementById("birth");
const address = document.getElementById("address");
const address_detail = document.getElementById("address_detail");
const zipcode = document.getElementById("zipcode");
const gender = document.getElementById("gender");

btn_submit.addEventListener("click", () => {
    if(!validation()){
        return;
    }
    customConfirm("수정 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        btn_submit.disabled=true;
    btn_address.disabled=true;
    membername.disabled=true;
    username.disabled=true;
    phone.disabled=true;
    birth.disabled=true;
    address.disabled=true;
    address_detail.disabled=true;
    zipcode.disabled=true;
    gender.disabled= true;
    $.ajax({
        type: "POST",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            "membername" : membername.value,
            "phone": phone.value,
            "birth":birth.value,
            "address": address.value,
            "address_detail": address_detail.value,
            "zipcode": zipcode.value,
            "gender": gender.value
        },
        datatype: "JSON",
        success: function(data) {
            customAlert(data.message, ()=>{
                location.href=data.url;
            });
        },
        error: function(error) {
            btn_submit.disabled=false;
            btn_address.disabled=false;
            membername.disabled=false;
            username.disabled=false;
            phone.disabled=false;
            birth.disabled=false;
            address.disabled=false;
            address_detail.disabled=false;
            zipcode.disabled=false;
            gender.disabled= false;
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

window.onload = function(){
    address.addEventListener("click", function(){
        //카카오 지도 발생
        new daum.Postcode({
            oncomplete: function(data) { //선택시 입력값 세팅
                address.value = data.address; // 주소 넣기
                zipcode.value = data.zonecode; // 우편번호 넣기
                address_detail.focus(); //상세입력 포커싱
            }
        }).open();
    });
    btn_address.addEventListener("click", function(){
        //카카오 지도 발생
        new daum.Postcode({
            oncomplete: function(data) { //선택시 입력값 세팅
                address.value = data.address; // 주소 넣기
                zipcode.value = data.zonecode; // 우편번호 넣기
                address_detail.focus(); //상세입력 포커싱
            }
        }).open();
    });
}

//전화번호 정규식
function regPhone(str){                                        
    let reg_phone = /^01([0-9]{1})([0-9]{4})([0-9]{4})$/;

    if(!reg_phone.test(str)){
       customAlert('유효하지 않은 전화번호 형식입니다. (-) 없이 입력 해주세요.');
       return false;
   }              
   return true;      
}

//유효성 체크 함수
function validation(){
    if(membername.value == ''){
        membername.focus();
        return false;
    }
    if(username.value == ''){
        username.focus();
        return false;
    }
    if(birth.value == ''){
        birth.focus();
        return false;
    }
    if(!regPhone(phone.value)){
        phone.focus();
        return false;
    }
    if(address.value == ''){
        address.focus();
        return false;
    }
    if(address_detail.value == ''){
        address_detail.focus();
        return false;
    }
    if(zipcode.value == ''){
        zipcode.focus();
        return false;
    }
    return true;
}