const textArea = document.getElementById('text_input');
const charCount = document.getElementById('char-count');
const clearBtn = document.getElementById('clear-text');
const demoBtn = document.getElementById('demo-fill');

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('image_file');
const browseBtn = document.getElementById('browse-btn');
const preview = document.getElementById('preview');

const modeButtons = document.querySelectorAll('.toggle-btn');
const textMode = document.getElementById('text-mode');
const imageMode = document.getElementById('image-mode');

const copyBtn = document.getElementById('copy-output');
const downloadBtn = document.getElementById('download-output');
const translatedBox = document.getElementById('translated-text');

// live char count
if (textArea && charCount) {
  const updateCount = () => { charCount.textContent = `${textArea.value.length} chars`; };
  updateCount();
  textArea.addEventListener('input', updateCount);
}

if (clearBtn && textArea) {
  clearBtn.addEventListener('click', () => {
    textArea.value = '';
    charCount.textContent = '0 chars';
    textArea.focus();
  });
}

if (demoBtn && textArea) {
  demoBtn.addEventListener('click', () => {
    textArea.value = 'Hello! Please translate this sentence to Nepali and French.';
    charCount.textContent = `${textArea.value.length} chars`;
  });
}

// mode switching (text / image)
modeButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    modeButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const mode = btn.dataset.mode;
    if (mode === 'text') {
      textMode.classList.add('active');
      imageMode.classList.remove('active');
    } else {
      imageMode.classList.add('active');
      textMode.classList.remove('active');
    }
  });
});

// dropzone behavior
if (dropzone && fileInput) {
  const openFilePicker = () => fileInput.click();

  dropzone.addEventListener('click', openFilePicker);
  if (browseBtn) browseBtn.addEventListener('click', openFilePicker);

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      fileInput.files = e.dataTransfer.files;
      showPreview(file);
    }
  });

  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file && file.type.startsWith('image/')) {
      showPreview(file);
    }
  });

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
}

// copy & download output
if (copyBtn && translatedBox) {
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(translatedBox.value);
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = 'Copy', 1200);
    } catch (e) {
      alert('Copy failed.');
    }
  });
}

if (downloadBtn && translatedBox) {
  downloadBtn.addEventListener('click', () => {
    const blob = new Blob([translatedBox.value || ''], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.download = 'translation.txt';
    a.href = url;
    a.click();
    URL.revokeObjectURL(url);
  });
}
