const option_name = document.getElementById("option_name");
const option_detail = document.getElementById("option_detail");

const btn_submit = document.getElementById("btn-submit");

btn_submit.addEventListener("click", () => {
    if(!validation()){
        return;
    }
    if(!confirm("등록 하시겠습니까?")) {
        return;
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
            alert(data.message);
            location.reload(true);
        },
        error: function(error) {
            btn_submit.disabled=false;
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

//유효성 체크 함수
function validation(){
    if(option_name.value == ''){
        option_name.focus();
        return false;
    }
    if(option_detail.value == ''){
        option_detail.focus();
        return false;
    }
    return true;
}

function deleteOption(id){
    if(!confirm("삭제 하시겠습니까?")) {
        return;
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
            alert(data.message);
            location.reload(true);
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


function createOptionDetail(id){
    if(!confirm("추가 하시겠습니까?")) {
        return;
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
            alert(data.message);
            location.reload(true);
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

function saveOptionDetail(id){
    if(!confirm("수정 하시겠습니까?")) {
        return;
    }
    let data = {
        "option_detail_id" : id,
        "option_name" : document.getElementById(`option_name_${id}`).value,
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
            alert(data.message);
            location.reload(true);
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


function deleteOptionDetail(id){
    if(!confirm("삭제 하시겠습니까?")) {
        return;
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
            alert(data.message);
            location.reload(true);
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
