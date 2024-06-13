const btn_delete = document.getElementById("btn-delete");

btn_delete.addEventListener("click", () => {
    if (!confirm("삭제 하시겠습니까?")) {
        return;
    }
    btn_delete.disabled=true;
    $.ajax({
        type: "DELETE",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        datatype: "JSON",
        success: function(data) {
            alert(data.message);
            location.href=data.url;
        },
        error: function(error) {
            btn_delete.disabled=false;
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