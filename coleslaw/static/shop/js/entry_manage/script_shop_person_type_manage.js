function shopEntryManage(reqType){
    if(!confirm("수정 하시겠습니까?")) {
        location.reload(true);
        return;
    }
    let data = {
        "reqType" : reqType
    }
    $.ajax({
        type: "PUT",
        url: '',
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
}