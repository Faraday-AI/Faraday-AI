def init_models():
    """Initialize and save AI models."""
    try:
        # Create models directory
        models_dir = Path("/app/app/models")  # Updated path
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize performance prediction model
        logger.info("Creating performance prediction model...")
        performance_model = create_dummy_performance_model()
        performance_model.save(str(models_dir / "performance_prediction.keras"), save_format='keras')
        logger.info("Performance prediction model saved successfully")
    except Exception as e:
        logger.error(f"Error initializing models: {e}")
        raise 