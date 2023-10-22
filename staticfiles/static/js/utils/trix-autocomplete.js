function AutoComplete(editor, editorElement, dropDownContainer, strategies) {
    this.editor = editor;
    this.editorElement = editorElement;
    this.dropDownContainer = dropDownContainer;
    this.strategies = strategies;
    this.autoCompleteOn = false;
    this.dropDownMenuActive = false;
    this.startingPosition = 0;
    this.endingPosition = 0;
    this.numDropDownItems = 0;
    this.currentStrategy = undefined;
  }
  
  AutoComplete.prototype.autoCompleteHandler = function () {
    this.documentString = this.editor.getDocument().toString();
    const position = this.editor.getPosition();
      
    // console.log("editor: ", this.dropDownContainer)
    this.dropDownContainer.style.display = 'none';
  
    if (position === 0) {
      this.autoCompleteOn = false;
      return;
    }
  
    this.checkAutoComplete(this.documentString[position - 1], position - 1);
  };
  
  AutoComplete.prototype.checkAutoComplete = function (currentString, position) {
    if (!currentString) {
      return;
    }
    this.autoCompleteOn = false;
    let searchForTrigger = true;
  
    this.endingPosition = position;
  
    const self = this;
  
    while (searchForTrigger) {
      if (currentString[0] === ' ') {
        searchForTrigger = false;
        break;
      } else if (position < 0) {
        searchForTrigger = false;
        break;
      }
      for (let i = 0; i < self.strategies.length; i++) {
        const strategy = self.strategies[i];
        if (strategy.trigger.test(currentString)) {
          searchForTrigger = false;
          this.autoCompleteOn = true;
          this.startingPosition = position;
          this.currentStrategy = strategy;
          this.searchTerm = currentString;
          break;
        }
      }
      position--;
      currentString = this.documentString[position] + currentString;
    }
    if (this.autoCompleteOn) {
      if (this.currentStrategy.index) {
        this.searchTerm = this.searchTerm.slice(this.currentStrategy.index);
      }
      this.currentStrategy.search(this.searchTerm, this.populateDropDown);
    }
  };
  
  AutoComplete.prototype.autoCompleteEnd = function () {
    this.autoCompleteOn = false;
    this.dropDownMenuActive = false;
    this.dropDownContainer.style.display = 'none';
    this.dropDownContainer.innerHTML = '';
  };
  
  AutoComplete.prototype.positionDropDown = function () {
    const domRange = this.editor.getClientRectAtPosition(this.editor.getPosition() - 1);
  
    if (!domRange || !this.dropDown) {
      return;
    }
  
    const topVal = domRange.top + domRange.height;
    const leftVal = domRange.left + domRange.width;
  
    this.dropDown.style.top = topVal + 'px';
    this.dropDown.style.left = leftVal + 'px';
    this.dropDown.style.position = 'fixed';
    this.dropDown.style.zIndex = '100';
  };
  
  AutoComplete.prototype.populateDropDown = function (results) {
    if (!results || !results.length || !this.autoCompleteOn) {
      return;
    }
    this.numDropDownItems = 0;
  
    this.dropDownContainer.innerHTML = "<ul class='dropdown-menu'></ul>";
    this.dropDown = document.querySelector('.dropdown-menu');
  
    this.positionDropDown();
  
    for (let i = 0; i < results.length; i++) {
      const result = results[i];
      const html = this.currentStrategy.template(result);
  
      const container = document.createElement('li');
      container.className = 'autoComplete-item';
      container.setAttribute('tabindex', '0');
      container.setAttribute('data-index', this.numDropDownItems);
      container.innerHTML = html;
  
      this.dropDown.appendChild(container);
      this.numDropDownItems++;
    }
    this.dropDownMenuActive = true;
    this.dropDownContainer.style.display = 'block';
  
    this.numDropDownItems = results.length;
    this.initEventListeners();
  };
  
  AutoComplete.prototype.insertAutoCompleteItem = function (dropDownItem) {
    let HTML;
    const startingPosition = this.startingPosition;
    const endingPosition = this.endingPosition;
    const currentStrategy = this.currentStrategy;
  
    if (currentStrategy.extract) {
      HTML = currentStrategy.extract(dropDownItem);
    } else {
      HTML = dropDownItem.innerText;
    }
  
    if (!HTML || endingPosition < startingPosition) {
      return;
    }
  
    this.editor.setSelectedRange([startingPosition, endingPosition + 1]);
    this.editor.deleteInDirection('forward');
  
    currentStrategy.replace(HTML, startingPosition);
  };
  
  AutoComplete.prototype.initEventListeners = function () {
    const self = this;
    const dropDownItemSelector = '.autoComplete-item';
    const dropDownItemJQ = document.querySelectorAll(dropDownItemSelector);
    dropDownItemJQ[0].focus();
  
    window.addEventListener('resize', function () {
      self.positionDropDown();
    });
  
    window.addEventListener('mousedown', function () {
      self.autoCompleteEnd();
    });
  
    document.querySelector('trix-editor').addEventListener('mousewheel', function () {
      self.autoCompleteEnd();
    });
  
    for (let i = 0; i < dropDownItemJQ.length; i++) {
      const dropDownItem = dropDownItemJQ[i];
      dropDownItem.addEventListener('mouseenter', function () {
        this.focus();
        this.classList.add('active');
      });
      dropDownItem.addEventListener('mouseleave', function () {
        this.classList.remove('active');
      });
      dropDownItem.addEventListener('mousedown', function () {
        self.insertAutoCompleteItem(this);
      });
      dropDownItem.addEventListener('keydown', function (event) {
        if (!self.dropDownMenuActive) {
          return;
        }
        const currentDataIndex = parseInt(this.getAttribute('data-index'));
        let nextDataIndex = 0;
        let jquerySelector;
  
        if (event.keyCode === 38) {
          if (currentDataIndex === 0) {
            nextDataIndex = self.numDropDownItems - 1;
          } else {
            nextDataIndex = currentDataIndex - 1;
          }
  
          jquerySelector = dropDownItemSelector + "[data-index='" + nextDataIndex + "']";
          this.blur();
          document.querySelector(jquerySelector).focus();
          event.preventDefault();
        } else if (event.keyCode === 40) {
          if (currentDataIndex === self.numDropDownItems - 1) {
            nextDataIndex = 0;
          } else {
            nextDataIndex = currentDataIndex + 1;
          }
  
          jquerySelector = dropDownItemSelector + "[data-index='" + nextDataIndex + "']";
          this.blur();
          document.querySelector(jquerySelector).focus();
          event.preventDefault();
        } else if (event.keyCode === 13 || event.keyCode === 9) {
          self.insertAutoCompleteItem(this);
          self.autoCompleteEnd();
          event.preventDefault();
          self.editorElement.focus();
        } else if (event.keycode === 16) {
          event.preventDefault();
        } else {
          self.autoCompleteEnd();
          self.editorElement.focus();
        }
      });
    }
  };
  