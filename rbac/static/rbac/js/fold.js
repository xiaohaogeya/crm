
$('.permission-area .parent').click(function () {
   $(this).find('.moca').toggleClass('fa-caret-right');
   // $(this).nextUntil('.parent').toggleClass('hidden');
   var mo = $(this).nextUntil('.parent').attr('hidden');
   if(mo){
      $(this).nextUntil('.parent').removeAttr('hidden');
   }else{
      $(this).nextUntil('.parent').attr('hidden','hidden');
   }
});