define(['jquery', 'js/lib/simplemde',
        'js/lib/foundation/foundation',
        'js/lib/foundation/foundation.dropdown',
        'js/lib/foundation/foundation.topbar'], function($, SimpleMDE) {
  var editor;

  console.log('editor active!');

  $(document).foundation();

  var simplemde = new SimpleMDE({
    element: document.getElementById("body")
  });

  $('#title-edit').change(function() {
    $('a[data-dropdown=\'title-drop\']').addClass('active');
    $('#title-label').text($('#title-edit').val());
  });
  $('#slug').change(function() {
    $('a[data-dropdown=\'slug-drop\']').addClass('active');
    $('#slug-label').text($('#slug').val());
  });
});
