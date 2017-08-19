
//获取窗口的高度 
var windowHeight; 
//获取窗口的宽度 
var windowWidth; 
//获取弹窗的宽度 
var popWidth; 
//获取弹窗高度 
var popHeight; 
function init(){ 
    windowHeight=$(window).height(); 
    windowWidth=$(window).width(); 
    popHeight=$(".window").height(); 
    popWidth=$(".window").width(); 
} 
//关闭窗口的方法 
function closeWindow(){ 
    $("#hide_window").hide();
} 
//定义弹出居中窗口的方法 
function popCenterWindow(){ 
    init(); 
    //计算弹出窗口的左上角Y的偏移量 
    var popY=(windowHeight-popHeight)/2; 
    var popX=(windowWidth-popWidth)/2; 
    //alert('jihua.cnblogs.com'); 
    //设定窗口的位置 
    var realNum = $("#realNum").val();
    $("#end").val(realNum);
    $("#hide_window").show();
    $("#loading").hide();
    $("#searching").hide();
    $("#approvalDiv").show();
    $("#center").css("top",popY).css("left",popX);  
    //closeWindow(); 
} 

// 加载
function popLoadingWindow(){ 
    init(); 
    //计算弹出窗口的左上角Y的偏移量 
    var popY=(windowHeight-popHeight)/2; 
    var popX=(windowWidth-popWidth)/2; 
    //alert('jihua.cnblogs.com'); 
    //设定窗口的位置
    $("#hide_window").show();
    $("#center").css("top",popY).css("left",popX);  
    $("#searching").show();
    $("#approvalDiv").hide();
    $("#loading").hide();
    //closeWindow(); 
} 




//==========================================================
// 首页ajax js
//===========================================================
function pre(){
  popLoadingWindow();
  var current_page = $("#current_page_hidden").val();
  current_page = parseInt(current_page);
  pre_page = current_page - 1;
  var isApproval = $("isApproval").val();

  if(isApproval == "1"){
    alert("前面内容已审核");
    return;
  }
  search(pre_page, next_page, "pre");

}

function next(){
  popLoadingWindow();
  var current_page = $("#current_page_hidden").val();
  current_page = parseInt(current_page);
  next_page = current_page + 1;
  $("isApproval").val("0");
  search(next_page, next_page, "next");
}

function do_search(){
     filter();
}

function filter_search(){
  $("#search_type").val("filter_search");
  filter();

}

function simple_search(){
  $("#search_type").val("simple_search");
  filter();
}

function filter(){
    $("#current_page_hidden").val(1);
    var label_state = $("#label_state").val();
    var user_role = $("#user_role").val();
    if(label_state == "2"){
        $("#approval_li").hide();
        $("#approval_div").hide();
    }else if (label_state == "1"){
        if(user_role == "1") {
            // 学生
           $("#preli").show();
           $("#nextli").show();
           $("#approval_li").hide();
           $("#approval_div").hide();
        }else{
          $("#approval_div").show();
            $("#approval_li").show();
        }
    }else{
        if(user_role == "1") {
            //学生
          $("#preli").hide();
          $("#nextli").hide();
        }
        $("#approval_div").show();
        $("#approval_li").show();
    }
    search(0,0, "filter");
}
function search(current_page, show_page, op){
  var search_type = $("#search_type").val();
  if(current_page < 0){
    alert("已经是第1页了");
    return;
  }
  var webs_chk=document.getElementsByName('webs');

  var webs=''; 
  var count = 0;
  for(var i=0; i<webs_chk.length; i++){ 
    if(webs_chk[i].checked){
       if(count == 0){
          webs += webs_chk[i].value; //如果选中，将value添加到变量s中
       }else{
          webs += "," + webs_chk[i].value; //如果选中，将value添加到变量s中
       }
       count = count + 1;
    } 
  }
  if(webs=='' && search_type == "filter_search"){
    alert("请选择新闻网站。"); 
    return;
  } else if (webs == '') {
     webs = 'xlw,xhs,fhw';
  }

  var label_states= get_check_val('label_state'); 
  if(label_states=='' && search_type == "filter_search"){
    alert("请选择新闻状态"); 
    return;
  } else if (label_states == '') {
    label_states="0,1,2";
  }

  var labels= get_check_val('labels'); 
  if(labels=='' && search_type == "filter_search"){
    alert("请选择新闻分类"); 
    return;
  } else if (labels=='') {
    labels = '0,1';
  }


  var tags = '';
  count = 0;
  var tags_chk = document.getElementsByName('tagselect');
  for(var i=0; i<tags_chk.length; i++){ 
    if(tags_chk[i].checked){
       if(count == 0){
          tags += tags_chk[i].value; //如果选中，将value添加到变量s中
       }else{
          tags += "," + tags_chk[i].value; //如果选中，将value添加到变量s中
       }
       count = count + 1;
    } 
  }

  var time_range_chk = document.getElementsByName('time_range_chk')
  var timerange_check = 0;
  if (time_range_chk[0].checked) {
     timerange_check = 1;
  }

  var page_size = $("#page_size").val();
  var timerange = $("#reservation").val();
  var search_key = $("#search_key").val();
  
  var label = $("#label").val();
  var label_state = $("#label_state").val();
  var article_db = 0;
  if($('#article_db').is(':checked')){
      article_db = 1;
  }
   popLoadingWindow();

  //location.href = "/search?current_page=" + current_page + "&webs=" + webs+"&page_size="+page_size;
  $.ajax({  
    type : "POST",  //提交方式  
    url : "/search",//路径  
    data : {  
       "current_page":current_page, "webs":webs, "page_size":page_size,
       "timerange":timerange, "article_db":article_db, "label_states":label_states,
       "label":labels, "search_key":search_key,"search_type":search_type,"tags":tags,
       "timerange_check":timerange_check
    },//数据，这里使用的是Json格式进行传输  
      success : function(result) {//返回数据根据结果进行相应的处理  
         if(result.length < 1 && current_page != 0){
           //$("nextli").addClass('disabled'); 
           if(op == "approval"){
             $("#showlist").html("");
           }
           alert("当前是最后一页");
           return;
         } 

         $("#current_page_num").html("<a>当前第"+ (show_page + 1) +"页</a>");
         $("#current_page_hidden").val(show_page);
         $("#showlist").empty();
         $("#showlist").empty();
         $("#showlist").empty();
         var tags = $("#tags").val()
         var tagsJson = $.parseJSON(''+tags+'');
         var realNum = result.length;
         $("#realNum").val(realNum);
          
         for(var i in result){ 
             var index = parseInt(i) + 1;
             var li_txt = '<li style=" margin: 5px 0px;" id="li_txt_'+i+'">'
             + '<div  id="atriclediv_'+i+'" style="">'  
             + '<h4><a id="title_a_'+i+'"   onclick="show_article('+i+')">['+index+']'
             + result[i].article_title + '</a></h4>' 
             + '<input type="hidden" id="label_hidden_'+i+'" value="'+result[i].article_label+'">'
             + '<input type="hidden" id="id_hidden_'+i+'" value="'+result[i].id+'">'
             + '<span>'+ result[i].article_publish_time+'</span>'
             + '来源:<span class="label label-primary">'+ result[i].article_source +'</span> &nbsp;&nbsp;分类:<span id="label_span_'+i+'">';
            if(result[i].article_label == 1){
              li_txt = li_txt + '<span class="label label-success">恐怖新闻</span>';
            }else{
               li_txt = li_txt + '<span class="label label-warning">非恐怖新闻</span>';
            }
            li_txt = li_txt + '</span> &nbsp;&nbsp;标签：<span id="tagsShow_'+i+'">';
            if (result[i].tags != undefined){  
                var tagslist = result[i].tags.split(',');
                for(var idx in tagslist){
                  if(tagslist[idx] != ""){
                    li_txt = li_txt + '&nbsp;<a class="glyphicon glyphicon-remove" style="color:black;text-decoration:none;" role="menuitem"  onclick="removeArticleTag(this,\''+i+'\')"><span class="label label-info">'+ tagslist[idx]+'</span></a>';
                  }
                }
               
            } 
            li_txt = li_txt + '</span>';
           if(result[i].update_student != undefined){
              li_txt = li_txt +'&nbsp;&nbsp;标注学生:<font style="color:red">' + result[i].update_student +"</font>";
            }
            if(result[i].update_admin != undefined){
              li_txt = li_txt + '&nbsp;&nbsp;审核管理员<font style="color:red">:'+  result[i].update_admin +"</font>";
            }  
            li_txt = li_txt + "<br/><p>"
            +'<span id="content_span_'+i+'">'
            + result[i].article_content + '</p></p></span></div>'
            + '<a class="btn btn-danger" onclick="changeLabel(\''+i+'\',\''+result[i].id+' \')" id="btn_change_'+i+'" role="button">纠正类标</a>&nbsp;&nbsp;'
            + '<div class="btn-group">'
            + '<select id="tags_'+ i +'" class="selectpicker show-tick form-control" name="tags_'+i+'">'
            + '<option value="0" ><a href="#"> &nbsp;&nbsp;&nbsp;</a></option>';
            for(var j in tagsJson){
               if(tagsJson[j].tag == "涉华恐怖袭击"){
                   li_txt = li_txt + '<option value="'+tagsJson[j].tag+'" selected="selected"><a href="#">'+ tagsJson[j].tag +'</a></option>';
               }else{
                  li_txt = li_txt + '<option value="'+tagsJson[j].tag+'"><a href="#">'+ tagsJson[j].tag +'</a></option>';
               }
               
            }
            li_txt = li_txt + '</select></div>'
            + '<a class="btn btn-default" onclick="addArticleTag(\''+i+'\')"  role="button">添加标签</a><br>'
            + '<div style="border-bottom: 1px dashed gray; height: 2px;" ></div></li>';
            $("#showlist").append(li_txt);    
         }
         
           closeWindow(); //关闭弹出的对话框
           if(op == "approval"){
              closeWindow(); //关闭弹出的对话框
           }
           $('body,html').animate({scrollTop:0},1000);
           //返回顶部
           var sc=$(window).scrollTop();
      }  
  });  
}

function get_check_val(elementName) {
  var check=document.getElementsByName(elementName);
  var content =''; 
  var count = 0;
  for(var i=0; i<check.length; i++){ 
    if(check[i].checked){
       if(count == 0){
          content += check[i].value; //如果选中，将value添加到变量s中
       }else{
          content += "," + check[i].value; //如果选中，将value添加到变量s中
       }
       count = count + 1;
    } 
  }
  return content;
}
function addArticleTag(itemId){
  var tagsId = "#tags_" + itemId;
  var tag_val = $(tagsId).val();
  var label = $("#label_hidden_"+itemId).val();
  var article_id = $("#id_hidden_"+itemId).val();
  if(tag_val == '0') {
    alert("请选择要添加的标签。");
    return;
  }
  $.ajax({  
    type : "GET",  //提交方式  
    url : "/addArticleTag",//路径  
    data : {  
       "tag":tag_val, "article_id":article_id, "label":label
    },//数据，这里使用的是Json格式进行传输  
      success : function(result) {//返回数据根据结果进行相应的处理  
         if(result == "success"){
             var spanVal = $("#tagsShow_" + itemId).html();
              spanVal = spanVal +'&nbsp;<a class="glyphicon glyphicon-remove" style="color:black;text-decoration:none;" role="menuitem"  onclick="removeArticleTag(this,\''+itemId+'\')"><span class="label label-info">'+ tag_val+'</span></a>';
             $("#tagsShow_" + itemId).html(spanVal);
         } 


      }  
  });  
}
function removeArticleTag(obj, itemId){
   if(!confirm("是否确认删除该标签？")){
      return;
   }
   var tag_val = $(obj).text();
   //$(obj).hide();
   var label = $("#label_hidden_"+itemId).val();
   var article_id = $("#id_hidden_"+itemId).val();
   $.ajax({  
    type : "GET",  //提交方式  
    url : "/removeArticleTag",//路径  
    data : {  
       "tag":tag_val, "article_id":article_id, "label":label
    },//数据，这里使用的是Json格式进行传输  
      success : function(result) {//返回数据根据结果进行相应的处理  
         if(result == "success"){
             $(obj).hide();
         } 
      }  
  });  

}

function changeLabel(itemId){
  var label = $("#label_hidden_"+itemId).val();
  var article_id = $("#id_hidden_"+itemId).val();
  var user_role = $("#user_role").val();
  var label_state = $("#label_state").val();
  if(label_state == "1" && user_role == '1'){
     if(!confirm("请确认是否修改？")){
        return;
     }
  }
  if(label_state == "2"){
     if(!confirm("请确认是否修改？")){
        return;
     }
  }

  $.ajax({  
    type : "GET",  //提交方式  
    url : "/changeLabel",//路径  
    data : {  
       "article_id":article_id, "label":label
    },//数据，这里使用的是Json格式进行传输  
      success : function(result) {//返回数据根据结果进行相应的处理 
        var obj = jQuery.parseJSON(result);
        var user_role = $("#user_role").val();
         if(obj.label == "1"){
            $("#label_span_"+itemId).html('<span class="label label-success">恐怖新闻</span>');
            $("#label_hidden_"+itemId).val("1");
            $("#id_hidden_"+itemId).val(obj.article_id);
            //$("#title_a_" + itemId).css("color","red");
            //$("#content_span_" + itemId).css("color","red");
            $("#li_txt_"+itemId).css("background-color","#98F898"); 

         }else if(obj.label == "0"){
             $("#label_span_"+itemId).html('<span class="label label-warning">非恐怖新闻</span>');
             $("#label_hidden_"+itemId).val("0");
             $("#id_hidden_"+itemId).val(obj.article_id);
             //$("#title_a_" + itemId).css("color","red");
             //$("#content_span_" + itemId).css("color","red");
             $("#li_txt_"+itemId).css("background-color","#98F898");

         }
         var btn_val = $("#btn_change_"+itemId).text();
         if(btn_val == "纠正类标"){
            $("#btn_change_"+itemId).removeClass();
            $("#btn_change_"+itemId).addClass("btn btn-default"); 
            $("#btn_change_"+itemId).text("取消纠正");
            $("#content_span_" + itemId).css("color","red");
            $("#title_a_" + itemId).css("color","red");
         }else{
           $("#btn_change_"+itemId).removeClass();
           $("#btn_change_"+itemId).addClass("btn btn-danger");
           $("#btn_change_"+itemId).text("纠正类标");
         }

      }  
  }); 

}
function show_article(itemId){
  var label = $("#label_hidden_"+itemId).val();
  var article_id = $("#id_hidden_"+itemId).val();
  //window.location.href ="/page?articleId="+article_id+ "&label="+label;
  window.open("/page?articleId="+article_id+ "&label="+label); 
}
function approvalAll(){
    var page_size = $("#realNum").val();
    var pageSize = parseInt(page_size);
    approval(0, pageSize);
}
function approvalPart(){
    var page_size = $("#realNum").val();
    var pageSize = parseInt(page_size);

    var begin = $("#begin").val();
    var end = $("#end").val();
    if(begin == "" || end == ""){
        alert("请输入起始序号！！");
    }
    var iBegin = parseInt(begin);
    var iEnd = parseInt(end);
    if(iEnd < iBegin){
        alert("结束序号必须大于开始序号");
        return;
    }
    if(iBegin < 0 ){
        iBegin = 0;
    }
    if(iEnd > pageSize){
        iEnd = pageSize;
    }
    approval(iBegin-1, iEnd);
}
 function approval(begin, end){
    if(end == 0) {
      alert("当前无数据，无法审核");
      return;
    }
    $("#loading").show();
    $("#approvalDiv").hide();
    var cur = 0;
    var count = end - begin;
    var flag = true;
    for(var i = begin; i < end; i++){
      var label = $("#label_hidden_"+i).val();
      var article_id = $("#id_hidden_"+i).val();
      if(label == undefined){
        break;
      }
      $.ajax({  
        type : "GET",  //提交方式  
        url : "/approval",//路径  
        data : {  
           "article_id":article_id, "label":label
        },//数据，这里使用的是Json格式进行传输  
          success : function(result) {//返回数据根据结果进行相应的处理 
            cur = cur + 1;
            var rate = cur/count;
            if(flag == true && rate == 1){
                var current_page = $("#current_page_hidden").val();
                current_page = parseInt(current_page);
                next_page = current_page + 1;
                $("isApproval").val("1");
                search(0, next_page, "approval");
                flag = false;
            }
          }  
      }); 
    }
    
}

        

  