String.prototype.replaceAt = function(index, replacement) {
    return this.substring(0, index) + replacement + this.substring(index + replacement.length);

  }

  document.querySelectorAll('.gallery__Image').forEach(
    function(original_img) {
      var img = new Image();
      img.onload = () => {
        if (img.width === 1 && img.height === 1) {
          original_img.remove();
        }
        else {
          original_img.classList.add("CORRECT");
          // _count = _count + 1;
          // changer = original_img.className.replace(/\d+/, _count)
        }
      }
      img.src = original_img.src;
      img.alt = 'Фотография авто';
  })
