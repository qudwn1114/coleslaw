const btn_delete = document.getElementById("btn-delete");

btn_delete.addEventListener("click", () => {
    customConfirm("삭제 하시겠습니까?")
    .then((result) => {
        if (!result) {
            return false;
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
            customAlert(data.message, ()=>{
                location.href=data.url;
            });
        },
        error: function(error) {
            btn_delete.disabled=false;
            if(error.status == 401){
                customAlert(i18n.login_required);
            }
            else if(error.status == 403){
                customAlert(i18n.no_permission);
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
    });
})