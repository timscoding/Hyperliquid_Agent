# Install pre-built wheels where possible
pip install --upgrade pip wheel setuptools

# Try installing pyswisseph with pre-built wheel
pip install pyswisseph --only-binary :all: 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "No pre-built pyswisseph available, trying alternative..."
    # Install specific version that might have wheels
    pip install pyswisseph==2.10.3.2 --only-binary :all: 2>$null
}

# For chromadb, use version with pre-built hnswlib
pip install chromadb==0.4.24 --only-binary :all: 2>$null

# Then install rest of requirements, skipping chromadb
pip install -r requirements.txt --ignore-installed chromadb pyswisseph kerykeion

# Finally try kerykeion again
pip install kerykeion
