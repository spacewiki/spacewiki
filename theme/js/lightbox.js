(function( ){
 $(document).ready(function() {
   $('img').each(function(idx, img) {
     var up = img.parentNode;
     up.setAttribute('data-lightbox', 'image');
     up.setAttribute('data-title', img.alt);
   })
 })
})();
