from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, get_cached_query
from models import UserModel
import time

router = APIRouter(
    prefix="/cache-test",
    tags=["caching"]
)

@router.get("/test-db-cache")
def test_db_cache(db: Session = Depends(get_db)):
    """
    Test endpoint to verify database caching is working.
    
    Makes the same query twice and measures execution time for each.
    The second call should be faster if caching is working properly.
    """
    # First query - should not be cached
    start_time = time.time()
    query = db.query(UserModel)
    results1 = get_cached_query(query).all()
    first_query_time = time.time() - start_time
    
    # Get cache stats before second query
    from database import get_db_cache_stats
    before_stats = get_db_cache_stats()
    
    # Second query - should be cached
    start_time = time.time()
    query = db.query(UserModel)
    results2 = get_cached_query(query).all()
    second_query_time = time.time() - start_time
    
    # Get cache stats after second query
    after_stats = get_db_cache_stats()
    
    # Calculate speed improvement
    if first_query_time > 0:
        speed_improvement = (first_query_time - second_query_time) / first_query_time * 100
    else:
        speed_improvement = 0
    
    return {
        "cache_working": after_stats["hits"] > before_stats["hits"],
        "first_query_time_ms": round(first_query_time * 1000, 2),
        "second_query_time_ms": round(second_query_time * 1000, 2),
        "speed_improvement_percent": round(speed_improvement, 2),
        "before_stats": before_stats,
        "after_stats": after_stats,
        "record_count": len(results1)
    }
