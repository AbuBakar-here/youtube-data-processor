// For Form validation

(function () {
  'use strict';
  window.addEventListener('load', function () {
    var forms = document.getElementsByClassName('needs-validation')
    var validation = Array.prototype.filter.call(forms, function (form) {
      form.addEventListener('submit', function (event) {
        if (form.checkValidity() === false) {
          event.preventDefault()
          event.stopPropagation()
        }
        form.classList.add('was-validated')
      }, false)
    })
  }, false)
})()



// for showing Modal when Page is loaded

$(document).ready(() => {
  // $('#myModal').modal('show')
})


// for removing newline from textare and replacing it with comma
var textarea = $('#textarea-for-keywords')

textarea.on('paste', () => {
  setTimeout(() => {
    var value = textarea.val().replaceAll('\n', ',')
    textarea.val(value)
  }, 0)
})

// For range Number
var range = $('#noOfResults')

range.on('change', () => {
  var rangeValue = range.val()
  $('label')[2].innerHTML = 'Number of Results: ' + rangeValue
})
