const btn_submit = document.getElementById("btn-submit");
const password = document.getElementById('password');
const new_password1 = document.getElementById('new_password1');
const new_password2 = document.getElementById('new_password2');

btn_submit.addEventListener("click", () => {
    const data =new FormData(document.getElementById("loginForm"));
    if(!validation()){
        return false
    }
    btn_submit.disabled=true;
    $.ajax({
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        url: "",
        data: data,
        enctype: "multipart/form-data", //form data 설정
        processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
        contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
        success: function(data) {
            alert(data.message);
            location.href = data.url;
        },
        error: function(error) {
            alert(error.responseJSON.message);
            btn_submit.disabled=false;
        },
    });
});

//유효성 체크 함수
function validation(){
    if(password.value == ''){
        password.focus();
        return false;
    }
    if(new_password1.value == ''){
        new_password1.focus();
        return false;
    }
    if(new_password2.value == ''){
        new_password2.focus();
        return false;
    }
    
    if(new_password1.value != new_password2.value){
        new_password1.focus();
        alert('비밀번호가 일치하지 않습니다.');
        return false;
    }
    if (!regPassword(new_password1.value)) {
        alert('비밀번호는 문자 숫자 조합으로 8 ~ 16 자리로 입력해주세요.');
        new_password1.focus();
        return false;
    }
    return true;
}

function regPassword(str) {
    if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d~#?!@$%^&*-+]{8,16}$/.test(str)) {
        return false;
    }
    return true;
}
