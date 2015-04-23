function useACE(yes) {
  console.log("ACE: %s", yes);
  if (yes) {
    $('#body').hide();
    $('#editor').show();
    $('#editor_toggle_value').value=true;
  } else {
    $('#body').show();
    $('#editor').hide();
    $('#editor_toggle_value').value=false;
  }
}

$(document).ready(function() {
  console.log($('#editor_toggle_value'));
  $('#editor_toggle_value').change(function() {
    useACE($('#editor_toggle_value')[0].checked);
  });
  if (ace) {
    $('#editor_toggle').show();
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode("ace/mode/markdown");
    editor.getSession().on('change', function(e) {
      $('#body').val(editor.getValue());
    });
    $('#body').changed(function() {
      editor.setValue($('#body').val());
    });
    useACE(true);
  }
});
