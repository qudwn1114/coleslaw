function setAdmin(id, elem){
    customConfirm(i18n.confirm_admin)
    .then((result) => {
        if (!result) {
        location.reload();
        return false;
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