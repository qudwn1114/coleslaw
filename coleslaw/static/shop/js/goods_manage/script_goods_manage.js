const main_category = document.getElementById("main_category");
const sub_category = document.getElementById("sub_category");
const search_form = document.getElementById("search-form");


let main_category_list = new Array();
let sub_category_list = new Array();

document.querySelectorAll('input[name="status"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      this.form.submit();
    });
});

//select box 초기화
function setCategory(type, arr){
    let $oSelect;
    if(type=='main'){
        $oSelect = $('#main_category');
    }
    else if(type=='sub'){
        $oSelect = $('#sub_category');
    }
    else{
        return;
    }
    $oSelect.empty();
    if(arr.length == 0){
        return;
    }
    $oSelect.removeAttr("disabled");
    for(let i=0; i<arr.length; i++){
        $oSelect.append(new Option(arr[i].name_kr , arr[i].id, false, false));
    }
    $oSelect.selectpicker('refresh');
}

function selectCategory(type, id, autoSubmit=true){
    let $sSelect = $('#sub_category');
    let filterArr = new Array();

    if(type=='main'){
        $sSelect.empty();
        $sSelect.attr("disabled", true);
        $sSelect.selectpicker('refresh');

        filterArr = sub_category_list.filter(function(elem){
            return elem.parent_id == id;
        });
        setCategory("sub", filterArr);
        if (autoSubmit) {
            search_form.submit();
        }        
    }
    else{
        if (autoSubmit) {
            search_form.submit();
        }     
        return;
    }
}

$(document).ready(function () {
    let queryString = new URLSearchParams(location.search);
    let url = '';
    if(queryString.toString()){
        document.getElementById("search_type").value = queryString.get("search_type");
        document.getElementById("search_keyword").value = queryString.get("search_keyword");
        if(queryString.get("status")){
            document.getElementById(`status${queryString.get("status")}`).checked=true;
        }
        let main_category_id = queryString.get("main_category_id");
        let sub_category_id = queryString.get("sub_category_id");
        if(main_category_id){
            // 카테고리 초기화
            $.ajax({
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                url: `/shop-manage/${shop_id}/category/`,
                success: function(data) {
                    main_category_list = data.main_category_list;
                    sub_category_list = data.sub_category_list;          
                    setCategory("main", main_category_list);
                    $('#main_category').val(main_category_id);
                    $('#main_category').selectpicker('refresh');
                    selectCategory('main', main_category_id, false);
                    if(sub_category_id){
                        $('#sub_category').val(sub_category_id);
                        $('#sub_category').selectpicker('refresh');
                    }
                },
                error: function(error) {
                    customAlert(error.status + error.responseJSON.message);
                },
            });
        }
        else{
            // 카테고리 초기화
            $.ajax({
                type: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                url: `/shop-manage/${shop_id}/category/`,
                success: function(data) {
                    main_category_list = data.main_category_list;
                    sub_category_list = data.sub_category_list;          
                    setCategory("main", main_category_list);  
                },
                error: function(error) {
                    customAlert(error.status + error.responseJSON.message);
                },
            });
        }
        url = `/shop-manage/${shop_id}/goods/?${queryString.toString()}`;
    }
    else{
         // 카테고리 초기화
         $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            url: `/shop-manage/${shop_id}/category/`,
            success: function(data) {
                main_category_list = data.main_category_list;
                sub_category_list = data.sub_category_list;          
                setCategory("main", main_category_list);  
            },
            error: function(error) {
                customAlert(error.status + error.responseJSON.message);
            },
        });
        document.getElementById("status1").checked=true;
        url = `/shop-manage/${shop_id}/goods/`;
    }
    $('#dataTables').DataTable({
        iDisplayLength: 20,
        aLengthMenu: [
            [20, 40, 60, 100], [20, 40, 60, 100]
        ],
        search: {
            return: true,
        },
        order: [[10, 'desc']],
        searching : false,
        processing: true,
        serverSide: true,
        scrollY: 650,
        scrollX: true,
        scrollCollapse: true,
        ajax: {
            "type" : "GET",
            "url" : url,
            "headers": {
                'X-CSRFToken': csrftoken
            },
        },
        columns: [
            { "data": "id", orderable: true },
            { "data": function(data, type, row){
                return `${data.mainCategoryNameKr}<br>${data.subCategoryNameKr}`;
                },
                orderable:false
            },

            { "data": function(data, type, row){
                    return `<a href="/shop-manage/${shop_id}/goods-detail/${data.id}?prev_url=${cur_url}">${truncateStr(data.name_kr, 18)}</a><p>${data.code}</p>`;
                }, 
                orderable: false 
            },
            { "data": function(data, type, row){
                    return `<img src="${data.imageThumbnailUrl}" width="50px"/>`;
                },
                orderable:false 
            },
            { "data": "price", orderable: false },
            { "data": function(data, type, row){
                    if(data.status){
                        return `<input class="form-check-input" type="checkbox" checked onclick="setStatus(${data.id}, 'STATUS', this)"/>`;
                    }
                    else{
                        return `<input class="form-check-input" type="checkbox" onclick="setStatus(${data.id}, 'STATUS', this)"/>`;
                    }
                },
                orderable: false 
            },
            { "data": function(data, type, row){
                    if(data.soldout){
                        return `<input class="form-check-input" type="checkbox" checked onclick="setStatus(${data.id}, 'SOLDOUT', this)"/>`;
                    }
                    else{
                        return `<input class="form-check-input" type="checkbox" onclick="setStatus(${data.id}, 'SOLDOUT', this)"/>`;
                    }
                },
                orderable: false 
            },
            { "data": function(data, type, row){
                    if(data.stock_flag){
                        return `<div class="input-group"><input class="form-control" type="number" value="${data.stock}" id="STOCK_${data.id}" onkeyup="enterkey(${data.id}, 'STOCK')"/><button class="btn btn-outline-secondary" type="button" id="btn_STOCK_${data.id}" onclick="setValue(${data.id}, 'STOCK', this)">${i18n.save}</button></div>`;
                    }
                    else{
                        return '<span>x</span>';
                    }
                },
                orderable: false 
            },
            { "data": function(data, type, row){
                    if(data.stock_flag){
                        return `<input class="form-check-input" type="checkbox" checked onclick="setStatus(${data.id}, 'STOCK_FLAG', this)"/>`;
                    }
                    else{
                        return `<input class="form-check-input" type="checkbox" onclick="setStatus(${data.id}, 'STOCK_FLAG', this)"/>`;
                    }
                },
                orderable: false 
            },
            { "data": function(data, type, row){
                    if(data.option_flag){
                        return `<input class="form-check-input" type="checkbox" checked onclick="setStatus(${data.id}, 'OPTION_FLAG', this)"/>`;
                    }
                    else{
                        return `<input class="form-check-input" type="checkbox" onclick="setStatus(${data.id}, 'OPTION_FLAG', this)"/>`;
                    }
                },
                orderable: false 
            },            
            { "data": "createdAt", orderable: true },
        ],
        columnDefs:
        [
            {
                targets: 0,
                visible:false
            },
            {
                targets: 4,
                render: function (data, type, row) {
                    return `<div class="input-group"><input class="form-control" type="number" value="${row.sale_price}" id="SALE_PRICE_${row.id}" onkeyup="enterkey(${row.id}, 'SALE_PRICE')"/><button class="btn btn-outline-secondary" type="button" id="btn_SALE_PRICE_${row.id}" onclick="setValue(${row.id}, 'SALE_PRICE', this)">${i18n.save}</button></div><div class="input-group"><input class="form-control" type="number" value="${data}" id="PRICE_${row.id}" onkeyup="enterkey(${row.id}, 'PRICE')"/><button class="btn btn-outline-secondary" type="button" id="btn_PRICE_${row.id}" onclick="setValue(${row.id}, 'PRICE', this)">${i18n.save}</button></div>`;
                },
                width: 200,
            },
            {
                targets: 7,
                width: 200,
            },

        ],  
    });
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function setStatus(id, type, elem){
    customConfirm(i18n.confirm_edit)
    .then((result) => {
        if (!result) {
            location.reload();
            return false;
        }
        let data = {
            goods_id : id,
            type : type
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
                location.reload(true);
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

function setValue(id, type, elem){
    customConfirm(i18n.confirm_edit)
    .then((result) => {
        if (!result) {
            location.reload();
            return false;
        }
        let input = document.getElementById(`${type}_${id}`);
    if (input.value == ''){
        input.focus();
        return;
    }
    let data = {
        goods_id : id,
        value : input.value,
        type : type
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
            location.reload(true);
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

function enterkey(id, type) {
    if (window.event.keyCode == 13) {
        let btn = document.getElementById(`btn_${type}_${id}`);
        setValue(id, type, btn);
    }
}

function truncateStr(str, n){
    return (str.length > n) ? str.slice(0, n-1) + '&hellip;' : str;
};