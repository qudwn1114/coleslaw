const main_category = document.getElementById("main_category");
const sub_category = document.getElementById("sub_category");

const goods_name_kr = document.getElementById("goods_name_kr");
const goods_name_en = document.getElementById("goods_name_en");
const price = document.getElementById("price");

const btn_submit = document.getElementById("btn-submit");


let main_category_list = new Array();
let sub_category_list = new Array();


window.onload = function(){
    // 카테고리 초기화
    $.ajax({
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        url: `/system-manage/category/`,
        success: function(data) {
            main_category_list = data.main_category_list;
            sub_category_list = data.sub_category_list;
        },
        error: function(error) {
            customAlert(error.status + error.responseJSON.message);
        },
    });
}

//select box 초기화
function setCategory(type, arr){
    let $oSelect;
    if(type=='main'){
        $oSelect = $('#main_category');
    }
    else if(type=='sub'){
        $oSelect = $('#sub_category');
    }
    else{
        return;
    }
    $oSelect.empty();
    if(arr.length == 0){
        return;
    }
    $oSelect.removeAttr("disabled");
    for(let i=0; i<arr.length; i++){
        $oSelect.append(new Option(arr[i].name_kr, arr[i].id, false, false));
    }
    $oSelect.selectpicker('refresh');
}

function selectCategory(type, id){
    let $sSelect = $('#sub_category');

    let filterArr = new Array();

    if(type=='main'){
        $sSelect.empty();
        $sSelect.attr("disabled", true);
        $sSelect.selectpicker('refresh');

        filterArr = sub_category_list.filter(function(elem){
            return elem.parent_id == id;
        });
        setCategory("sub", filterArr);
        sub_category.focus(); 
    }
    else{
        return;
    }
}


btn_submit.addEventListener("click", () => {
    if(!validation()){
        return;
    }
    customConfirm("수정 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        const data =new FormData(document.getElementById("data-form"));
    btn_submit.disabled=true;
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
    if(sub_category.value == ''){
        sub_category.focus();
        customAlert('상품은 소분류까지 분류되어야합니다.');
        return false;
    }
    if(goods_name_kr.value == ''){
        goods_name_kr.focus();
        return false;
    }
    if(goods_name_en.value == ''){
        goods_name_en.focus();
        return false;
    }
    if(price.value == '' || price.value < 0){
        price.focus();
        return false;
    }
    return true;
}