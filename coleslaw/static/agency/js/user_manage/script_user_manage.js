function xlsxDownload(){
    customConfirm(i18n.save_excel)
        .then((result) => {
            if (!result) {
            return false;
            }
            if(window.location.search){
                console.log(window.location.search);
                strurl = window.location.pathname + window.location.search;
                window.location.href= strurl + '&excel=excel';
            }
            else{
                console.log(window.location.search);
                strurl = window.location.pathname;
                window.location.href= strurl + '?excel=excel';
            }
        });
}




function changeActive(id, checkbox){
    if(checkbox.checked){
        var text = "활성";
        var status = 1;
    }else{
        var text = "비활성";
        var status = 0;
    }


    customConfirm(i18n.confirm_edit)
        .then((result) => {
        if (!result) {
            // 취소한 경우, 스타일 및 체크 상태 복원
            if (text === "활성") {
            checkbox.parentElement.classList.remove("btn-primary");
            checkbox.parentElement.classList.add("btn-light", "off");
            } else {
            checkbox.parentElement.classList.remove("btn-light", "off");
            checkbox.parentElement.classList.add("btn-primary");
            }
            checkbox.checked = !checkbox.checked;
            return false;
        } 
        $.ajax({
            type: "PUT",
            url: "",
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({ 
                "type" : "ACTIVE",
                "user_id" : id,
                "is_active" : status
            }),
            datatype: "JSON",
            success: function(data) {
                location.reload(true);
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
                if(checkbox.checked){
                    checkbox.parentElement.classList.remove("btn-primary");
                    checkbox.parentElement.classList.add("btn-light","off");
                }else{
                    checkbox.parentElement.classList.remove("btn-light", "off");
                    checkbox.parentElement.classList.add("btn-primary");
                }
                checkbox.checked = !checkbox.checked
            },
        });
    });
}


function setAdmin(id, elem){
    customConfirm(i18n.confirm_admin)
    .then((result) => {
        if (!result) {
            location.reload();
            return false;
        }
        let data = {
            type : "ADMIN",
            user_id : id
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