(function( ){
 $(document).ready(function() {
   $('#content img').each(function(idx, img) {
     var up = img.parentNode;
     up.setAttribute('data-lightbox', 'image');
     up.setAttribute('data-title', img.alt);
   })
 })
})();
