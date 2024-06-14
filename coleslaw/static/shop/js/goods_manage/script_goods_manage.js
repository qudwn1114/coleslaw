const main_category = document.getElementById("main_category");
const sub_category = document.getElementById("sub_category");

let main_category_list = new Array();
let sub_category_list = new Array();

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
        $oSelect.append(new Option(arr[i].name , arr[i].id, false, false));
    }
    $oSelect.selectpicker('refresh');
}

function selectCategory(type, id){
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
        sub_category.focus();
        
    }
    else{
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
                url: `/system-manage/category/`,
                success: function(data) {
                    main_category_list = data.main_category_list;
                    sub_category_list = data.sub_category_list;          
                    setCategory("main", main_category_list);
                    $('#main_category').val(main_category_id);
                    $('#main_category').selectpicker('refresh');
                    selectCategory('main', main_category_id);
                    if(sub_category_id){
                        $('#sub_category').val(sub_category_id);
                        $('#sub_category').selectpicker('refresh');
                    }
                },
                error: function(error) {
                    alert(error.status + error.responseJSON.message);
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
                url: `/system-manage/category/`,
                success: function(data) {
                    main_category_list = data.main_category_list;
                    sub_category_list = data.sub_category_list;          
                    setCategory("main", main_category_list);  
                },
                error: function(error) {
                    alert(error.status + error.responseJSON.message);
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
            url: `/system-manage/category/`,
            success: function(data) {
                main_category_list = data.main_category_list;
                sub_category_list = data.sub_category_list;          
                setCategory("main", main_category_list);  
            },
            error: function(error) {
                alert(error.status + error.responseJSON.message);
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
        order: [[6, 'desc']],
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
            { "data": "name", orderable: true },
            { "data": function(data, type, row){
                    return `<img src="${data.imageThumbnailUrl}" width="50px"/>`;
                },
                orderable:false 
            },
            { "data": "price", orderable: false },
            { "data": "goodsStatus", orderable: false },
            { "data": function(data, type, row){
                    if(data.isEntryGoods){
                        return `<input class="form-check-input" type="checkbox" checked onclick="setEntryGoods(${data.id}, this)"/>`;
                    }
                    else{
                        return `<input class="form-check-input" type="checkbox" onclick="setEntryGoods(${data.id}, this)"/>`;
                    }
                },
                orderable: true 
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
                targets: 1,
                render: function (data, type, row) {
                    return `<a href="/shop-manage/${shop_id}/goods-detail/${row.id}">${data}</a>`;
                }
            },
            {
                targets: 3,
                render: function ( data, type, row ) {
                    return numberWithCommas(data);
                }
            },

        ],  
    });
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function setEntryGoods(id, elem){
    if (!confirm("입장 상품을 수정하시겠습니까?")) {
        location.reload();
        return;
    }
    let data = {
        goods_id : id,
        type : "ENTRYGOODS"
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