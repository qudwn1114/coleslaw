const btn_submit = document.getElementById("btn-submit");
const btn_address = document.getElementById("btn-address")
const representative = document.getElementById("representative");
const shop_category_id = document.getElementById("shop_category_id");
const shop_name_kr = document.getElementById("shop_name_kr");
const shop_name_en = document.getElementById("shop_name_en");
const description = document.getElementById("description");
const phone = document.getElementById("phone");
const registration_no = document.getElementById("registration_no");
const address = document.getElementById("address");
const address_detail = document.getElementById("address_detail");
const zipcode = document.getElementById("zipcode");
const image = document.getElementById("image");
const location_image = document.getElementById("location_image");
const main_tid = document.getElementById("main_tid");
const waiting_time = document.getElementById("waiting_time");
const logo_image1 = document.getElementById("logo_image1");
const entry_image1 = document.getElementById("entry_image1");
const logo_image2 = document.getElementById("logo_image2");
const entry_image2 = document.getElementById("entry_image2");
const table_time = document.getElementById('table_time');
const additional_fee_time = document.getElementById('additional_fee_time');

btn_submit.addEventListener("click", () => {
    if(!validation()){
        return;
    }
    if (!confirm("가입 하시겠습니까?")) {
        return;
    }
    const data =new FormData(document.getElementById("data-form"));
    btn_submit.disabled=true;
    btn_address.disabled=true;
    representative.disabled=true;
    shop_category_id.disabled=true;
    shop_name_kr.disabled=true;
    shop_name_en.disabled=true;
    description.disabled=true;
    phone.disabled=true;
    registration_no.disabled=true;
    address.disabled=true;
    address_detail.disabled=true;
    zipcode.disabled=true;
    image.disabled=true;
    location_image.disabled=true;
    main_tid.disabled=true;
    waiting_time.disabled=true;
    logo_image1.disabled=true;
    entry_image1.disabled=true;
    logo_image2.disabled=true;
    entry_image2.disabled=true;
    table_time.disabled=true;
    additional_fee_time.disabled=true;
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
            alert(data.message);
            location.href=data.url;
        },
        error: function(error) {
            btn_submit.disabled=false;
            btn_address.disabled=false;
            representative.disabled=false;
            shop_category_id.disabled=false;
            shop_name_kr.disabled=false;
            shop_name_en.disabled=false;
            description.disabled=false;
            phone.disabled=false;
            registration_no.disabled=false;
            address.disabled=false;
            address_detail.disabled=false;
            zipcode.disabled=false;
            image.disabled=false;
            location_image.disabled=false;
            main_tid.disabled=false;
            waiting_time.disabled=false;
            logo_image1.disabled=false;
            entry_image1.disabled=false;
            logo_image2.disabled=false;
            entry_image2.disabled=false;
            table_time.disabled=false;
            additional_fee_time.disabled=false;
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
    let reg_phone = /^[0-9]*$/;
    if(!reg_phone.test(str)){
       alert('유효하지 않은 전화번호 형식입니다. (-) 없이 입력 해주세요.');
       return false;
   }              
   return true;      
}

//유효성 체크 함수
function validation(){
    if(shop_category_id.value == ''){
        shop_category_id.focus();
        return false;
    }
    if(shop_name_kr.value == ''){
        shop_name_kr.focus();
        return false;
    }
    if(shop_name_en.value == ''){
        shop_name_en.focus();
        return false;
    }
    if(!regPhone(phone.value)){
        phone.focus();
        return false;
    }
    return true;
}

function SetNum(obj){
    val=obj.value;
    re=/[^0-9]/gi;
    obj.value=val.replace(re,""); 
}