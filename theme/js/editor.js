(function() {
  var editor;
  var editor_stream;
  var editor_key = Math.random();

  $(document).ready(function() {$(document).foundation();});

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
      editor.getSession().getDocument().setValue($('#body').val());
  }

  function syncEditorToBody() {
    $('#body').val(editor.getValue());
  }

  $(document).ready(function() {
    $(document).foundation();
  });

  var _eventLock = true;

  function broadcastChange(delta) {
    if (_eventLock)
      return;
    var signature = Math.random();
    editor_stream.emit('message', 'foo');
    editor_stream.emit('text_delta', {delta: delta.data, key: editor_key, signature: signature});
    console.log('send delta', delta);
  }

  function broadcastCursorEvent(evt) {
    var cursor = editor.getSelection().getCursor();
    editor_stream.emit('message', 'foo');
    editor_stream.emit('cursor', {key: editor_key, row: cursor.row, column:cursor.column});
    console.log('send cursor', evt);
  }

  function handleDeltaEvent(message) {
    if (message.key != editor_key) {
      _eventLock = true;
      editor.getSession().getDocument().applyDeltas([message.delta]);
      _eventLock = false;
      console.log(message.delta);
    }
  }

  function handleCursorEvent(message) {
    if (message.key != editor_key) {
      pos = editor.renderer.textToScreenCoordinates(message.row, message.column);
      if (!markers.hasOwnProperty(message.key)) {
        var marker = document.createElement("div");
        marker.setAttribute('class', 'human-marker');
        var randomColor = Math.floor(Math.random()*16777215).toString(16);
        marker.setAttribute('style', 'background-color:#'+randomColor);
        $('.editor-row').prepend(marker);
        markers[message.key] = marker;
      }
      $(markers[message.key]).offset({left:pos.pageX, top:pos.pageY + $(document).scrollTop()});
    }
  }

  var markers = {};

  window.require(['ace/ace', 'ace/theme/monokai', 'ace/mode/markdown'], function(ace) {
    if ($('#editor').length > 0) {
      if (typeof(ace) != 'undefined') {
        $('#editor_toggle').show();
        editor = ace.edit("editor");

        editor_stream = io.connect('http://'+document.domain+':'+location.port+'/editor');
        editor_stream.on('text_delta', handleDeltaEvent);
        editor_stream.on('cursor', handleCursorEvent);
        editor.setTheme("ace/theme/monokai");
        editor.getSession().setMode("ace/mode/markdown");
        editor.getSession().getDocument().on('change', broadcastChange);
        editor.getSession().getDocument().on('change', syncEditorToBody);
        editor.getSelection().on('changeCursor', broadcastCursorEvent);
        editor.getSession().setUseWrapMode(true);
        $('#body').change(syncBodyToEditor);
        $.cookie.json = true;
        if ($.cookie('use-ace')) {
          useACE(true);
        } else {
          useACE(false);
        }
      } else {
        console.log('No ace found');
      }
      syncBodyToEditor();
      _eventLock = false;
      $('#editor_toggle_value').change(function() {
        useACE($('#editor_toggle_value')[0].checked);
      });
      $('#body').change(updatePreview);
      updatePreview();
    } else {
      console.log('No editor found');
    }
  });

  $('#title-edit').change(function() {
    $('a[data-dropdown=\'title-drop\']').addClass('active');
    $('#title-label').text($('#title-edit').val());
  });
  $('#slug').change(function() {
    $('a[data-dropdown=\'slug-drop\']').addClass('active');
    $('#slug-label').text($('#slug').val());
  });
})();
