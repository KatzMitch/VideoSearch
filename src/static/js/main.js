$(document).ready(function() {
  $("body").on('click', 'div.result-card', function() {
    $(this).siblings().removeClass("active");
    $("video").each(function() {
      $(this).get(0).pause();
    });

    $(this).addClass("active");
    video = $(this).find("video");
    video.get(0).play();
  })
});