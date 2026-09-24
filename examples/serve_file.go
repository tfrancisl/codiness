package files

import (
	"os"
	"path/filepath"
)

// ReadUpload returns the contents of a file inside the uploads directory.
func ReadUpload(baseDir, name string) ([]byte, error) {
	return os.ReadFile(filepath.Join(baseDir, name))
}
