function shopEntryManage(reqType){
    customConfirm("수정 하시겠습니까?")
    .then((result) => {
        if (!result) {
            location.reload();
            return false;
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
                customAlert(data.message, ()=>{
                    location.reload(true);
                });
            },
            error: function(error) {
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
}