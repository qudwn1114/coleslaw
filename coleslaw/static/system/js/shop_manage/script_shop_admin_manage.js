function setAdmin(id, elem){
    if (!confirm("관리자 지정을 수정하시겠습니까?")) {
        location.reload();
        return;
    }
    let data = {
        id : id
    };
    elem.disabled=true;
    $.ajax({
        type: "POST",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: data,
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                location.reload();
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}