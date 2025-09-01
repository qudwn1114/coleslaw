function setStatus(id, elem){
    customConfirm(i18n.confirm_edit)
    .then((result) => {
        if (!result) {
            location.reload();
            return false;
        }
        let data = {
            type : "STATUS",
            shop_id : id
        };
        elem.disabled=true;
        $.ajax({
            type: "PUT",
            url: "",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify(data),
            datatype: "JSON",
            success: function(data) {
                location.reload();
            },
            error: function(error) {
                elem.disabled=false;
                if(error.status == 401){
                    customAlert(i18n.login_required);
                }
                else if(error.status == 403){
                    customAlert(i18n.no_permission);
                }
                else{
                    customAlert(error.status + JSON.stringify(error.responseJSON), ()=>{
                        location.reload();
                    });
                }
            },
        });
    });
}