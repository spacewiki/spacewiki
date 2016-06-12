(function() {
  var editor;

  function useACE(yes) {
    console.log("ACE: %s", yes);
    if (yes) {
      $('#body').hide();
      $('#editor').show();
      $('#editor_toggle_value')[0].checked = true;
      $.cookie('use-ace', true);
    } else {
      $('#body').show();
      $('#editor').hide();
      $('#editor_toggle_value')[0].checked = false;
      $.cookie('use-ace', false);
    }
  }

  function updatePreview() {
    $.post('/preview', {'body': $('#body').val(), 'slug': $('#slug').val()}).then(function (data) {
      $('.preview').html(data);
    });
  }

  function syncBodyToEditor() {
    if (editor)
      editor.setValue($('#body').val());
  }

  function syncEditorToBody() {
    $('#body').val(editor.getValue());
  }

  $(document).ready(function() {
    $(document).foundation();
  });

  window.require(['ace/ace', 'ace/theme/monokai', 'ace/mode/markdown'], function(ace) {
    if ($('#editor').length > 0) {
      if (typeof(ace) != 'undefined') {
        $('#editor_toggle').show();
        editor = ace.edit("editor");
        editor.setTheme("ace/theme/monokai");
        editor.getSession().setMode("ace/mode/markdown");
        editor.getSession().on('change', syncEditorToBody);
        $('#body').change(syncBodyToEditor);
        $.cookie.json = true;
        if ($.cookie('use-ace')) {
          useACE(true);
        } else {
          useACE(false);
        }
      }
      syncBodyToEditor();
      $('#editor_toggle_value').change(function() {
        useACE($('#editor_toggle_value')[0].checked);
      });
      $('#body').change(updatePreview);
      updatePreview();
    }
  });
})();
