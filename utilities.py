from datetime import datetime, timedelta


def get_relative_timespan(time_span):
    current_timespan = datetime.now()
    compare_timespan = datetime.now()

    match time_span:
        case "day":
            current_timespan -= timedelta(days=1)
            compare_timespan = current_timespan - timedelta(days=1)
        case "week":
            current_timespan -= timedelta(weeks=1)
            compare_timespan = current_timespan - timedelta(weeks=1)

        case "month":
            current_timespan -= timedelta(weeks=4)
            compare_timespan = current_timespan - timedelta(weeks=4)

        case "year":
            current_timespan -= timedelta(weeks=52)
            compare_timespan = current_timespan - timedelta(weeks=52)
    return current_timespan,compare_timespan
    
    
    