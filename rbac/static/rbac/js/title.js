    $('.item .title').click(function () {
       $(this).next().toggleClass('hidden').parent().siblings().children('.body').addClass('hidden');

    });