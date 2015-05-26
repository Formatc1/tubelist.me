window.addEventListener('load', init, false);

function init(){
  $( ".cross" ).hide();
  $( "#playlist_nav" ).hide();
  $( ".hamburger" ).click(function() {
    $( "#playlist_nav" ).slideToggle( "fast", function() {
      $( ".hamburger" ).hide();
      $( ".cross" ).show();
    });
  });

  $( ".cross" ).click(function() {
    $( "#playlist_nav" ).slideToggle( "fast", function() {
      $( ".cross" ).hide();
      $( ".hamburger" ).show();
    });
  });

}