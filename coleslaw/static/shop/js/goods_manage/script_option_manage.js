const option_name_kr = document.getElementById("option_name_kr");
const option_name_en = document.getElementById("option_name_en");
const option_detail = document.getElementById("option_detail");

const btn_submit = document.getElementById("btn-submit");

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
            location.reload(true);
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
    if(option_name_kr.value == ''){
        option_name_kr.focus();
        return false;
    }
    if(option_name_en.value == ''){
        option_name_en.focus();
        return false;
    }
    if(option_detail.value == ''){
        option_detail.focus();
        return false;
    }
    return true;
}

function deleteOption(id){
    customConfirm("삭제 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        $.ajax({
            type: "DELETE",
            url: "",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({"option_id" : id}),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}


function createOptionDetail(id){
    customConfirm("추가 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        $.ajax({
            type: "POST",
            url: `/shop-manage/${shop_id}/option-detail-manage/`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {"option_id" : id},
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}

function saveOptionDetail(id){
    customConfirm("수정 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        let data = {
            "type": "DETAIL",
            "option_detail_id" : id,
            "option_name_kr" : document.getElementById(`option_name_kr_${id}`).value,
            "option_name_en" : document.getElementById(`option_name_en_${id}`).value,
            "option_price" : document.getElementById(`option_price_${id}`).value,
            "option_stock" : document.getElementById(`option_stock_${id}`).value
        }
        $.ajax({
            type: "PUT",
            url: `/shop-manage/${shop_id}/option-detail-manage/`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify(data),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}


function deleteOptionDetail(id){
    customConfirm("삭제 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
        }
        $.ajax({
            type: "DELETE",
            url: `/shop-manage/${shop_id}/option-detail-manage/`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({"option_detail_id" : id}),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}


function setStockFlag(id, elem){
    customConfirm("옵션재고 관리 설정을 변경하시겠습니까?")
    .then((result) => {
        if (!result) {
            location.reload(true);
            return false;
        }
        let data = {
            "type": "STOCK_FLAG",
            "option_detail_id" : id
        }
        $.ajax({
            type: "PUT",
            url: `/shop-manage/${shop_id}/option-detail-manage/`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify(data),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}

function setRequired(id){
    customConfirm("옵션필수 선택을 수정하시겠습니까?")
    .then((result) => {
        if (!result) {
            location.reload(true);
            return false;
        }
        $.ajax({
            type: "PUT",
            url: "",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({"option_id" : id}),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}


function setSoldout(id, elem){
    customConfirm("품절 상태를 변경하시겠습니까?")
    .then((result) => {
        if (!result) {
            location.reload(true);
            return false;
        }
        let data = {
            "type": "SOLD_OUT",
            "option_detail_id" : id
        }
        $.ajax({
            type: "PUT",
            url: `/shop-manage/${shop_id}/option-detail-manage/`,
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify(data),
            datatype: "JSON",
            success: function(data) {
                customAlert(data.message);
                location.reload(true);
            },
            error: function(error) {
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
}