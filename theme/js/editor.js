(function() {

  var EditSession = function(nacl, editor) {
      this.nacl = nacl
      this.markers = {};
      this.editor = editor;

      this._eventLock = false;

      this.keys = this.nacl.crypto_sign_keypair();
      this.hexPubKey = this.nacl.to_hex(this.keys.signPk);

      this.stream = io.connect('http://'+document.domain+':'+location.port+'/editor');

      this.stream.on('text_delta', this.handleDelta.bind(this));
      this.stream.on('cursor', this.handleCursor.bind(this));

      var doc = this.editor.getSession().getDocument();
      doc.on('change', this.broadcastChange.bind(this));
      doc.on('change', this.syncToBody.bind(this));

      var selection = this.editor.getSelection();
      selection.on('changeCursor', this.broadcastCursorEvent.bind(this));

      this.syncFromBody();
  }

  EditSession.prototype.verifyEvent = function(evt) {
      var pubkey = this.nacl.from_hex(evt.key);
      var verified = this.nacl.decode_utf8(this.nacl.crypto_sign_open(this.nacl.from_hex(evt.payload), pubkey));
      if (!verified) {
          console.log("Could not verify event from", evt.key, evt.payload);
          return false;
      }
      return JSON.parse(verified);
  }

  EditSession.prototype.sendEvent = function(evtType, payload) {
    var encoded = this.nacl.encode_utf8(JSON.stringify(payload));
    var signed = this.nacl.crypto_sign(encoded, this.keys.signSk);
    var bundle = {
        payload: this.nacl.to_hex(signed),
        key: this.hexPubKey
    };
    this.stream.emit(evtType, bundle);
  }

  EditSession.prototype.broadcastCursorEvent = function(evt) {
      var cursor = this.editor.getSelection().getCursor();
      this.sendEvent('cursor', {row: cursor.row, column:cursor.column});
  }

  EditSession.prototype.broadcastChange = function(delta) {
      if (this._eventLock)
          return;
      this.sendEvent('text_delta', {delta: delta.data});
  }

  EditSession.prototype.handleDelta = function(message) {
      var parsed = this.verifyEvent(message);
      if (!parsed) {
          return;
      }
      if (message.key != this.hexPubKey) {
          this._eventLock = true;
          this.editor.getSession().getDocument().applyDeltas([parsed.delta]);
          this._eventLock = false;
          console.log(parsed.delta);
      }
  }

  EditSession.prototype.handleCursor = function(message) {
      var parsed = this.verifyEvent(message);
      if (!parsed) {
          return;
      }
      if (message.key != this.hexPubKey) {
          pos = this.editor.renderer.textToScreenCoordinates(parsed.row, parsed.column);
          if (!this.markers.hasOwnProperty(message.key)) {
              var marker = document.createElement("div");
              marker.setAttribute('class', 'human-marker');
              var randomColor = Math.floor(Math.random()*16777215).toString(16);
              marker.setAttribute('style', 'background-color:#'+randomColor);
              $('.editor-row').prepend(marker);
              this.markers[message.key] = marker;
          }
          $(this.markers[message.key]).offset({left:pos.pageX, top:pos.pageY + $(document).scrollTop()});
      }
  }

  EditSession.prototype.syncFromBody = function() {
      this.editor.getSession().getDocument().setValue($('#body').val());
  }

  EditSession.prototype.syncToBody = function() {
      $('#body').val(this.editor.getValue());
  }

  function updatePreview() {
    $.post('/preview', {'body': $('#body').val(), 'slug': $('#slug').val()}).then(function (data) {
      $('.preview').html(data);
    });
  }

  $(document).ready(function() {
    $(document).foundation();
  });

  var session;

  window.require(['ace/ace', 'ace/theme/monokai', 'ace/mode/markdown'], function(ace) {
    if ($('#editor').length > 0) {
        var editor = ace.edit("editor");

        nacl_factory.instantiate(function(nacl) {
            session = new EditSession(nacl, editor);
        });

        editor.setTheme("ace/theme/monokai");
        editor.getSession().setMode("ace/mode/markdown");
        editor.getSession().setUseWrapMode(true);

        $('.editor-row .tabs').on('toggled', function(event, tab) {
            if (tab.innerText == "Preview") {
                updatePreview();
            }
        });
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
