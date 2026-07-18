from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.model import train_model


if __name__ == "__main__":
    result = train_model()
    print(f"Training samples: {result.samples}")
    print(f"Validation accuracy: {result.accuracy:.3f}")
    print(f"Saved model: {result.model_path}")
    print(result.report)
