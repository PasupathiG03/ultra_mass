def pastdate_userwise_report6(db: Session, picked_date: str, to_date: str) -> list:
    '''entity hold status utilization'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []

    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date(),
            models.TL.work_status == "Hold"  # Filter for work status
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
            
            if tl_record:
                scope = db.query(models.scope).filter(models.scope.scope_id == tl_record.Scope).first()
                subscope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == tl_record.From).first()
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                createddate = tl_record.created_on.strftime("%Y-%m-%d") if tl_record.created_on else "Unknown"
                completeddate = tl_record.completed_time.strftime("%Y-%m-%d") if tl_record.completed_time else "Unknown"
            else:
                scope, subscope, nature_of_work, entity = None, None, None, "Unknown"

            # Set in_progress_time based on the condition
            in_progress_time = record.total_inprogress_time if status == "Hold" else "00:00:00"

            # Exclude specific remarks
            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Append each service record to the daily_summaries list
            daily_summaries.append({
                'date': current_day.strftime("%Y-%m-%d"),
                'Serviced_id': service_id,
                'entity': entity,
                'scope': scope.scope if scope else "Unknown",  # Assuming 'scope' is the correct field name
                'subscope': subscope.sub_scope if subscope else "Unknown",  # Assuming 'sub_scope' is the correct field name
                'nature_of_work': nature_of_work.work_name if nature_of_work else "Unknown",  
                'total_time': in_progress_time,
                'Worked_By': username,
                'Created_Date': createddate,
                'Remarks': remarks,
                'status': status
            })

        current_day += timedelta(days=1)

    return daily_summaries


-----


def pastdate_userwise_report7(db: Session, picked_date: str, to_date: str) -> list:
    '''entity wise totaltimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    report_entries = []
    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                gstintan = tl_record.gst_or_tan
                count = tl_record.no_of_items

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "Non-Charchable":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
            else:
                entity = None
                status = "Unknown"
                gstintan = "Unknown"
                chargable_time = "00:00:00"
                non_chargable_time = "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(non_chargable_time)
            total_time = seconds_to_time(total_seconds)

            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Create a report entry for each record
            report_entry = {
                'date': current_day.strftime("%Y-%m-%d"),
                'username': username,
                'service_id': service_id,
                'entity': entity,
                'GSTIN/TAN': gstintan,
                'Chargable_Time': chargable_time,
                'Non_Chargable_Time': non_chargable_time,
                'Total_Time': total_time,
                'Count': count,
                'Remarks': remarks,
            }

            # Append each entry to the report list
            report_entries.append(report_entry)

        current_day += timedelta(days=1)

    return report_entries


--------


def pastdate_userwise_report8(db: Session, picked_date: str, to_date: str) -> list:
    '''entity cum natureofwork wise totaltimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id

            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()

            chargable_time = "00:00:00"
            Non_Chargable_Time = "00:00:00"

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                gstintan = tl_record.gst_or_tan
                Count = tl_record.no_of_items
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "Non-Charchable":
                    Non_Chargable_Time = record.total_inprogress_time or "00:00:00"
            else:
                entity = None
                status = "Unknown"
                gstintan = "Unknown"
                chargable_time = "00:00:00"
                Non_Chargable_Time = "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(Non_Chargable_Time)
            total_time = seconds_to_time(total_seconds)

            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Append each service entry as a separate dictionary
            daily_summaries.append({
                "date": current_day.strftime("%Y-%m-%d"),
                "username": username,
                "Serviced_id": service_id,
                "entity": entity,
                "GSTIN/TAN": gstintan,
                "nature_of_work": nature_of_work.work_name if nature_of_work else "Unknown",
                "Chargable_Time": chargable_time,
                "Non_Chargable_Time": Non_Chargable_Time,
                "Total_Time": total_time,
                "Count": Count,
                "Remarks": remarks,
            })

        current_day += timedelta(days=1)

    return daily_summaries



-------


from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta

def pastdate_userwise_report9(db: Session, picked_date: str, to_date: str) -> list:
    '''scopewisetimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []

    current_day = picked_datett
    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(dict))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            Non_Chargable_Time = "00:00:00"
            entity = None

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL

                scope = db.query(models.scope).filter(models.scope.scope_id == tl_record.Scope).first()

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "Non-Charchable":
                    Non_Chargable_Time = record.total_inprogress_time or "00:00:00"
                
                # Fetch the scope name
                scope_name = scope.scope if scope else "Unknown"
            else:
                scope_name = "Unknown"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Aggregate time for the username and scope
            user_times[scope_name]['Chargable_Time'] = (
                seconds_to_time(time_to_seconds(user_times[scope_name].get('Chargable_Time', "00:00:00")) + time_to_seconds(chargable_time))
            )
            user_times[scope_name]['Non_Chargable_Time'] = (
                seconds_to_time(time_to_seconds(user_times[scope_name].get('Non_Chargable_Time', "00:00:00")) + time_to_seconds(Non_Chargable_Time))
            )

            # Calculate total time in seconds
            total_seconds = time_to_seconds(user_times[scope_name]['Chargable_Time']) + time_to_seconds(user_times[scope_name]['Non_Chargable_Time'])
            user_times[scope_name]['Total_Time'] = seconds_to_time(total_seconds)

        # Only add the summary if there was data for the day
        if user_times:
            for scope_name, times in user_times.items():
                daily_summaries.append({
                    "date": current_day.strftime("%Y-%m-%d"),
                    "Nature_of_Scope": scope_name,
                    "Chargable_Time": times['Chargable_Time'],
                    "Non_Chargable_Time": times['Non_Chargable_Time'],
                    "Total_Time": times['Total_Time']
                })

        current_day += timedelta(days=1)

    return daily_summaries


-----
def pastdate_userwise_report10(db: Session, picked_date: str, to_date: str) -> dict:
    '''scope cum subscope timetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []  # Changed to a list to hold each day's summaries
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            entity = None

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL

                scope = db.query(models.scope).filter(models.scope.scope_id == tl_record.Scope).first()
                subscope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == tl_record.From).first()

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "Non-Charchable":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
                
                # Fetch the scope name
                scope_name = scope.scope if scope else "Unknown"
                subscope_name = subscope.sub_scope if subscope else "unknown"  
            else:
                scope_name = "Unknown"
                subscope_name = "unknown"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Aggregate times
            user_times[username][scope_name][subscope_name][service_id] = {
                'in_progress': record.total_inprogress_time or "00:00:00",
                'entity': entity,
                'scope': scope_name,
                'subscope': subscope_name,
                'Chargable_Time': chargable_time,
                'Non_Chargable_Time': non_chargable_time,
                'Total_Time': "00:00:00"  # Initialize Total_Time to zero
            }

        # Aggregate the totals for each user, scope, and subscope
        for username, scopes in user_times.items():
            for scope_name, subscopes in scopes.items():
                for subscope_name, services in subscopes.items():
                    total_chargable_seconds = 0
                    total_non_chargable_seconds = 0

                    for service_id, times in services.items():
                        total_chargable_seconds += time_to_seconds(times['Chargable_Time'])
                        total_non_chargable_seconds += time_to_seconds(times['Non_Chargable_Time'])
                        # Update the in_progress and entity if needed
                        user_times[username][scope_name][subscope_name][service_id]['Total_Time'] = times['Total_Time']

                    # Set aggregated Chargable and Non-Chargable Time
                    aggregated_chargable_time = seconds_to_time(total_chargable_seconds)
                    aggregated_non_chargable_time = seconds_to_time(total_non_chargable_seconds)

                    # Update the first entry for the subscope with aggregated times
                    user_times[username][scope_name][subscope_name]['Chargable_Time'] = aggregated_chargable_time
                    user_times[username][scope_name][subscope_name]['Non_Chargable_Time'] = aggregated_non_chargable_time
                    user_times[username][scope_name][subscope_name]['Total_Time'] = seconds_to_time(total_chargable_seconds + total_non_chargable_seconds)

        # Only add the summary if there was data for the day
        if user_times:
            for username, scopes in user_times.items():
                for scope_name, subscopes in scopes.items():
                    for subscope_name, services in subscopes.items():
                        formatted_day_summary = {
                            "date": current_day.strftime("%Y-%m-%d"),  # Date as a key-value pair
                            "nature_of_scope": scope_name,
                            "subscope": subscope_name,
                            'Chargable_Time': user_times[username][scope_name][subscope_name]['Chargable_Time'],
                            'Non_Chargable_Time': user_times[username][scope_name][subscope_name]['Non_Chargable_Time'],
                            'Total_Time': user_times[username][scope_name][subscope_name]['Total_Time'],  # Fetch Total_Time from user_times
                        }

                        daily_summaries.append(formatted_day_summary)  # Add each entry to the list

        current_day += timedelta(days=1)

    return daily_summaries
-----



def pastdate_userwise_report11(db: Session, picked_date: str, to_date: str) -> dict:
    '''subscope wise timetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []  # Changed to a list to hold each day's summaries
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            entity = None

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL

                scope = db.query(models.scope).filter(models.scope.scope_id == tl_record.Scope).first()
                subscope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == tl_record.From).first()

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "Non-Charchable":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
                
                # Fetch the scope name
                scope_name = scope.scope if scope else "Unknown"
                subscope_name = subscope.sub_scope if subscope else "unknown"  
            else:
                scope_name = "Unknown"
                subscope_name = "unknown"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Aggregate times
            user_times[username][scope_name][subscope_name][service_id] = {
                'in_progress': record.total_inprogress_time or "00:00:00",
                'entity': entity,
                'scope': scope_name,
                'subscope': subscope_name,
                'Chargable_Time': chargable_time,
                'Non_Chargable_Time': non_chargable_time,
                'Total_Time': "00:00:00"  # Initialize Total_Time to zero
            }

        # Aggregate the totals for each user, scope, and subscope
        for username, scopes in user_times.items():
            for scope_name, subscopes in scopes.items():
                for subscope_name, services in subscopes.items():
                    total_chargable_seconds = 0
                    total_non_chargable_seconds = 0

                    for service_id, times in services.items():
                        total_chargable_seconds += time_to_seconds(times['Chargable_Time'])
                        total_non_chargable_seconds += time_to_seconds(times['Non_Chargable_Time'])
                        # Update the in_progress and entity if needed
                        user_times[username][scope_name][subscope_name][service_id]['Total_Time'] = times['Total_Time']

                    # Set aggregated Chargable and Non-Chargable Time
                    aggregated_chargable_time = seconds_to_time(total_chargable_seconds)
                    aggregated_non_chargable_time = seconds_to_time(total_non_chargable_seconds)

                    # Update the first entry for the subscope with aggregated times
                    user_times[username][scope_name][subscope_name]['Chargable_Time'] = aggregated_chargable_time
                    user_times[username][scope_name][subscope_name]['Non_Chargable_Time'] = aggregated_non_chargable_time
                    user_times[username][scope_name][subscope_name]['Total_Time'] = seconds_to_time(total_chargable_seconds + total_non_chargable_seconds)

        # Only add the summary if there was data for the day
        if user_times:
            for username, scopes in user_times.items():
                for scope_name, subscopes in scopes.items():
                    for subscope_name, services in subscopes.items():
                        formatted_day_summary = {
                            "date": current_day.strftime("%Y-%m-%d"),  # Date as a key-value pair
                            "nature_of_scope": scope_name,
                            "subscope": subscope_name,
                            'Chargable_Time': user_times[username][scope_name][subscope_name]['Chargable_Time'],
                            'Non_Chargable_Time': user_times[username][scope_name][subscope_name]['Non_Chargable_Time'],
                            'Total_Time': user_times[username][scope_name][subscope_name]['Total_Time'],  # Fetch Total_Time from user_times
                        }

                        daily_summaries.append(formatted_day_summary)  # Add each entry to the list

        current_day += timedelta(days=1)

    return daily_summaries


--------
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException

def pastdate_userwise_report12(db: Session, picked_date: str, to_date: str) -> list:
    '''subscope cum natureofwork wise timetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            entity = None

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                Count = tl_record.no_of_items
                scope = db.query(models.scope).filter(models.scope.scope_id == tl_record.Scope).first()
                subscope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == tl_record.From).first()

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
                
                # Fetch the scope name
                scope_name = scope.scope if scope else "Unknown"
                subscope_name = subscope.sub_scope if subscope else "unknown"  
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()

            else:
                scope_name = "Unknown"
                subscope_name = "unknown"
                nature_of_work = "unknown"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Aggregate times
            user_times[username][scope_name][subscope_name][nature_of_work.work_name if nature_of_work else "Unknown"][service_id] = {
                'in_progress': record.total_inprogress_time or "00:00:00",
                'entity': entity,
                'Chargable_Time': chargable_time,
                "Count": Count,
                'Non_Chargable_Time': non_chargable_time,
                'Total_Time': "00:00:00"  # Initialize Total_Time to zero
            }

        # Aggregate the totals for each user, scope, subscope, and nature_of_work
        for username, scopes in user_times.items():
            for scope_name, subscopes in scopes.items():
                for subscope_name, nature_of_work_dict in subscopes.items():
                    for nature_of_work_name, services in nature_of_work_dict.items():
                        total_chargable_seconds = 0
                        total_non_chargable_seconds = 0

                        for service_id, times in services.items():
                            total_chargable_seconds += time_to_seconds(times['Chargable_Time'])
                            total_non_chargable_seconds += time_to_seconds(times['Non_Chargable_Time'])
                            # Update the in_progress and entity if needed
                            user_times[username][scope_name][subscope_name][nature_of_work_name][service_id]['Total_Time'] = times['Total_Time']

                        # Set aggregated Chargable and Non-Chargable Time
                        aggregated_chargable_time = seconds_to_time(total_chargable_seconds)
                        aggregated_non_chargable_time = seconds_to_time(total_non_chargable_seconds)

                        # Append the result to daily_summaries
                        daily_summaries.append({
                            "date": current_day.date(),
                            "nature_of_scope": scope_name,
                            "subscope": subscope_name,
                            "natureofwork": nature_of_work_name,
                            "Chargable_Time": aggregated_chargable_time,
                            "Non_Chargable_Time": aggregated_non_chargable_time,
                            "Count": Count,
                            "Total_Time": seconds_to_time(total_chargable_seconds + total_non_chargable_seconds),
                        })

        current_day += timedelta(days=1)

    # Return the daily summaries directly
    return daily_summaries
-----

from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta

def pastdate_userwise_report13(db: Session, picked_date: str, to_date: str) -> list:
    '''entity cum serviceid wise estimatedtime vs totaltimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []  # Change to a list
    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            estimated_time = "00:00:00"  # Initialize estimated_time

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                gstintan = tl_record.gst_or_tan
                Count = tl_record.no_of_items
                
                
                # Get estimated time from TL
                estimated_time = tl_record.estimated_time if tl_record.estimated_time else "00:00:00"

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
            else:
                entity = None
                gstintan = "Unknown"
                chargable_time = "00:00:00"
                non_chargable_time = "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(non_chargable_time)
            total_time = seconds_to_time(total_seconds)

            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Append the result to daily_summaries list
            daily_summaries.append({
                "username": username,
                "data": current_day.strftime("%Y-%m-%d"),
                "entity": entity,
                "GSTIN/TAN": gstintan,
                "Service_ID": service_id,
                "Estimated_Time": estimated_time,
                "Chargable_Time": chargable_time,
                "Non_Chargable_Time": non_chargable_time,
                "Total_Time": total_time,
                "Count": Count,
                "Remarks": remarks,
            })

        current_day += timedelta(days=1)

    return daily_summaries


------


def pastdate_userwise_report33(db: Session, picked_date: str, to_date: str) -> list:
    '''Entity-wise estimated time vs total time taken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            username = db.query(models.User_table.username).filter(
                models.User_table.user_id == record.user_id
            ).scalar() or "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            estimated_time = "00:00:00"  # Initialize estimated_time

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                gstintan = tl_record.gst_or_tan
                Count = tl_record.no_of_items
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                
                # Get estimated time from TL
                estimated_time = tl_record.estimated_time if tl_record.estimated_time else "00:00:00"

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"
            else:
                entity = None
                status = "Unknown"
                gstintan = "Unknown"
                chargable_time = "00:00:00"
                non_chargable_time = "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(non_chargable_time)
            total_time = seconds_to_time(total_seconds)

            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Append the summary for this service to the daily_summaries list
            daily_summaries.append({
                "username": username,
                "data": current_day.strftime("%Y-%m-%d"),
                "entity": entity,
                "GSTIN/TAN": gstintan,
                "nature_of_work": nature_of_work.work_name if nature_of_work else "Unknown",
                "Estimated_Time": estimated_time,
                "Chargable_Time": chargable_time,
                "Non_Chargable_Time": non_chargable_time,
                "Total_Time": total_time,
                "Service_ID": service_id,
                "Count": Count,
                "Remarks": remarks,
            })

        current_day += timedelta(days=1)

    return daily_summaries
-------

from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta

def pastdate_userwise_report14(db: Session, picked_date: str, to_date: str) -> list:
    '''teammember cum entity wise totaltimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    report_data = []  # Initialize a list to store the output
    current_day = picked_datett

    while current_day <= to_datett:
        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch first name and last name from the User_table and concatenate them
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()
            username = f"{user_info.firstname} {user_info.lastname}" if user_info else "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()

            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            estimated_time = "00:00:00"  # Initialize estimated_time
            entity = None
            status = "Unknown"
            gstintan = "Unknown"

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                gstintan = tl_record.gst_or_tan
                estimated_time = tl_record.estimated_time if tl_record.estimated_time else "00:00:00"

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(non_chargable_time)
            total_time = seconds_to_time(total_seconds)

            # Create a report entry
            report_entry = {
                "data": current_day.strftime("%Y-%m-%d"),
                "Name_of_the_team_Member": username,
                "entity": entity,
                "GSTIN/TAN": gstintan,
                "Chargable_Time": chargable_time,
                "Non_Chargable_Time": non_chargable_time,
                "Total_Time": total_time,
                "Service_ID": service_id,
            }
            report_data.append(report_entry)  # Append the entry to the report list

        current_day += timedelta(days=1)

    return report_data



-------


from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

def pastdate_userwise_report15(db: Session, picked_date: str, to_date: str):
    '''Teammember cum natureofwork wise totaltimetaken'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        # Dictionary to hold user times grouped by nature_of_work
        user_times = defaultdict(lambda: defaultdict(lambda: {
            'Chargable_Time': "00:00:00",
            'Non_Chargable_Time': "00:00:00",
            'Total_Time': "00:00:00",
        }))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch user information from the User_table
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()
            username = f"{user_info.firstname} {user_info.lastname}" if user_info else "Unknown"

            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == record.service_id).first()
            nature_of_work = "Unknown"

            if tl_record:
                # Get the nature of work
                nature_of_work_record = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                nature_of_work = nature_of_work_record.work_name if nature_of_work_record else "Unknown"

                # Determine Chargable_Time and Non_Chargable_Time based on type of activity
                total_in_progress_time = record.total_inprogress_time or "00:00:00"
                if tl_record.type_of_activity == "CHARGABLE":
                    user_times[username][nature_of_work]['Chargable_Time'] = seconds_to_time(
                        time_to_seconds(user_times[username][nature_of_work]['Chargable_Time']) + 
                        time_to_seconds(total_in_progress_time)
                    )
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    user_times[username][nature_of_work]['Non_Chargable_Time'] = seconds_to_time(
                        time_to_seconds(user_times[username][nature_of_work]['Non_Chargable_Time']) + 
                        time_to_seconds(total_in_progress_time)
                    )

            # Calculate Total_Time by summing both Chargable_Time and Non_Chargable_Time
            user_times[username][nature_of_work]['Total_Time'] = seconds_to_time(
                time_to_seconds(user_times[username][nature_of_work]['Chargable_Time']) + 
                time_to_seconds(user_times[username][nature_of_work]['Non_Chargable_Time'])
            )

        # Only add the summary if there was data for the day
        if user_times:
            for username, nature_data in user_times.items():
                for nature_of_work, times in nature_data.items():
                    daily_summaries.append({
                        'data': current_day.strftime("%Y-%m-%d"),  # Include the date
                        'Name_of_the_team_Member': username,
                        'nature_of_work': nature_of_work,
                        'Chargable_Time': times['Chargable_Time'],
                        'Non_Chargable_Time': times['Non_Chargable_Time'],
                        'Total_Time': times['Total_Time']
                    })

        current_day += timedelta(days=1)

    # Return the daily summaries directly
    return daily_summaries  # Return the list directly

# Function to convert time strings to seconds
def time_to_seconds(time_str):
    if time_str == "00:00:00":
        return 0
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60 + seconds

# Function to convert seconds back to HH:MM:SS
def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"




------

def pastdate_userwise_report16(db: Session, picked_date: str, to_date: str) -> dict:
    '''Teammember cum natureofwork wise estimatedtime vs chargable'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: {
            'Name_of_Team_member': None,
            'nature_of_work': None,
            'Estimated_Time': "00:00:00",
            'Chargable_Time': "00:00:00",
            'Difference': "00:00:00",
        })

        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        for record in records:
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()
            username = f"{user_info.firstname} {user_info.lastname}" if user_info else "Unknown"
            service_id = record.service_id
            
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            estimated_time = "00:00:00"

            if tl_record:
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                
                estimated_time = tl_record.estimated_time if tl_record.estimated_time else "00:00:00"

                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"

            if nature_of_work:
                work_name = nature_of_work.work_name
                user_times[work_name]['Name_of_Team_member'] = username
                user_times[work_name]['nature_of_work'] = work_name

                user_times[work_name]['Estimated_Time'] = seconds_to_time(
                    time_to_seconds(user_times[work_name]['Estimated_Time']) + time_to_seconds(estimated_time)
                )
                user_times[work_name]['Chargable_Time'] = seconds_to_time(
                    time_to_seconds(user_times[work_name]['Chargable_Time']) + time_to_seconds(chargable_time)
                )

                # Calculate the difference between Estimated_Time and Chargable_Time
                estimated_seconds = time_to_seconds(user_times[work_name]['Estimated_Time'])
                chargable_seconds = time_to_seconds(user_times[work_name]['Chargable_Time'])
                difference_seconds = estimated_seconds - chargable_seconds
                
                user_times[work_name]['Difference'] = seconds_to_time(max(difference_seconds, 0))  # Ensure no negative values

        # Instead of appending to a list, construct the desired output format
        for times in user_times.values():
            if times['Name_of_Team_member']:  # Ensure that the team member is valid
                daily_summaries.append({
                    "data": current_day.strftime("%Y-%m-%d"),
                    "Name_of_the_team_Member": times['Name_of_Team_member'],
                    "nature_of_work": times['nature_of_work'],
                    "Estimated_Time": times['Estimated_Time'],
                    "Chargable_Time": times['Chargable_Time'],
                    "Difference": times['Difference']
                })

        current_day += timedelta(days=1)

    return daily_summaries  # Return the list of summaries

# Helper functions remain unchanged
def time_to_seconds(time_str):
    # Handle cases with different time formats
    time_parts = list(map(int, time_str.split(':')))
    if len(time_parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = time_parts
    elif len(time_parts) == 2:  # MM:SS
        hours, minutes, seconds = 0, time_parts[0], time_parts[1]
    elif len(time_parts) == 1:  # SS
        hours, minutes, seconds = 0, 0, time_parts[0]
    else:
        return 0  # Invalid format, return 0 seconds
    
    return hours * 3600 + minutes * 60 + seconds

def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"
-------

def pastdate_userwise_report17(db: Session, picked_date: str, to_date: str) -> list:
    '''Team member cum nature of work wise estimated time vs total time'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []  # Changed from OrderedDict to list
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(dict))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()
            if user_info:
                username = f"{user_info.firstname} {user_info.lastname}"  # Concatenate first and last names
            else:
                username = "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
            chargable_time = "00:00:00"
            non_chargable_time = "00:00:00"
            estimated_time = "00:00:00"  # Initialize estimated_time

            if tl_record:
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
                gstintan = tl_record.gst_or_tan
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                
                # Get estimated time from TL
                estimated_time = tl_record.estimated_time if tl_record.estimated_time else "00:00:00"

                # Determine Chargable_Time based on type of activity
                if tl_record.type_of_activity == "CHARGABLE":
                    chargable_time = record.total_inprogress_time or "00:00:00"
                elif tl_record.type_of_activity == "NONCHARGABLE":
                    non_chargable_time = record.total_inprogress_time or "00:00:00"

            # Function to convert time strings to seconds
            def time_to_seconds(time_str):
                if time_str == "00:00:00":
                    return 0
                hours, minutes, seconds = map(int, time_str.split(':'))
                return hours * 3600 + minutes * 60 + seconds

            # Function to convert seconds back to HH:MM:SS
            def seconds_to_time(seconds):
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total time in seconds
            total_seconds = time_to_seconds(chargable_time) + time_to_seconds(non_chargable_time)
            total_time = seconds_to_time(total_seconds)

            # Populate user_times dictionary
            user_times[username][service_id] = {
                'in_progress': record.total_inprogress_time or "00:00:00",
                'nature_of_work': nature_of_work.work_name if nature_of_work else "Unknown",  
                'entity': entity,
                'workstatus': status,
                'gst': gstintan,
                'Chargable_Time': chargable_time,
                'Non_Chargable_Time': non_chargable_time,
                'Total_Time': total_time,  # Add Total_Time here
                'Estimated_Time': estimated_time  # Add Estimated_Time here
            }

        # Add the records to daily_summaries list
        for username in user_times:
            for service_id in user_times[username]:
                record_summary = {
                    "date": current_day.strftime("%Y-%m-%d"),
                    "service_id": service_id,
                    "Name_of_Team_member": username,
                    "entity": user_times[username][service_id]['entity'],
                    "GSTIN/TAN": user_times[username][service_id]['gst'],
                    "nature_of_work": user_times[username][service_id]['nature_of_work'],
                    "Estimated_Time": user_times[username][service_id]['Estimated_Time'],
                    "Chargable_Time": user_times[username][service_id]['Chargable_Time'],
                    "Non_Chargable_Time": user_times[username][service_id]['Non_Chargable_Time'],
                    "Total_Time": user_times[username][service_id]['Total_Time'],
                }
                daily_summaries.append(record_summary)  # Append each summary to the list

        current_day += timedelta(days=1)

    return daily_summaries



------


def pastdate_userwise_report18(db: Session, picked_date: str, to_date: str) -> list:
    '''Teammember cum natureofwork with No.of.Entity'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []
    current_day = picked_datett

    while current_day <= to_datett:
        nature_of_work_times = defaultdict(lambda: defaultdict(lambda: {
            'total_time': timedelta(),  # Initialize total_time as timedelta
            'entities': set()
        }))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()
            if user_info:
                username = f"{user_info.firstname} {user_info.lastname}"  # Concatenate first and last names
            else:
                username = "Unknown"

            service_id = record.service_id

            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()

            if tl_record:
                nature_of_work = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id == tl_record.nature_of_work).first()
                entity = tl_record.name_of_entity  # Assuming this is directly from TL
                status = tl_record.work_status
            else:
                nature_of_work, entity = None, "Unknown"

            in_progress_time = "00:00:00" if status == "completed" else record.total_inprogress_time or "00:00:00"
            in_progress_timedelta = timedelta(hours=int(in_progress_time.split(':')[0]),
                                               minutes=int(in_progress_time.split(':')[1]),
                                               seconds=int(in_progress_time.split(':')[2]))

            # Populate nature_of_work_times dictionary, grouping by nature_of_work first
            nature_of_work_name = nature_of_work.work_name if nature_of_work else "Unknown"

            # Aggregate data by nature_of_work and username
            user_work_data = nature_of_work_times[nature_of_work_name][username]
            user_work_data['total_time'] += in_progress_timedelta  # Aggregate total time
            user_work_data['entities'].add(entity)  # Add entity to the set of distinct entities

        # Only add the summary if there was data for the day
        for nature_of_work in nature_of_work_times:
            for username, user_work_data in nature_of_work_times[nature_of_work].items():
                daily_summaries.append({
                    'Name_of_teammember': username,
                    'nature_of_work': nature_of_work,
                    'total_time': str(user_work_data['total_time']),  # Convert timedelta to string or format as needed
                    'no.of.entity': len(user_work_data['entities'])  # Count distinct entities
                })

        current_day += timedelta(days=1)

    # Directly return the list of daily summaries
    return daily_summaries
# ------


def pastdate_userwise_report19(db: Session, picked_date: str, to_date: str) -> dict:
    '''Entity-wise estimated vs actual date of delivery'''
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    daily_summaries = []  # Change to a list for desired output format
    current_day = picked_datett

    while current_day <= to_datett:
        user_times = defaultdict(lambda: defaultdict(dict))

        # Query total time taken for the current day and join with TL table
        records = db.query(models.TotalTimeTaken).join(
            models.TL, models.TotalTimeTaken.service_id == models.TL.Service_ID
        ).filter(
            models.TotalTimeTaken.date == current_day.date()
        ).all()

        # Process the records
        for record in records:
            # Fetch username from the User_table
            user_info = db.query(models.User_table).filter(
                models.User_table.user_id == record.user_id
            ).first()

            username = f"{user_info.firstname} {user_info.lastname}" if user_info else "Unknown"

            service_id = record.service_id
            
            # Fetch additional fields from TL
            tl_record = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
            Count = tl_record.no_of_items if tl_record else "Unknown"
            entity = tl_record.name_of_entity if tl_record else "Unknown"
            gstintan = tl_record.gst_or_tan if tl_record else "Unknown"
            nature_of_work = db.query(models.Nature_Of_Work).filter(
                models.Nature_Of_Work.work_id == tl_record.nature_of_work
            ).first() if tl_record else None
            estimated_d_o_d = tl_record.estimated_d_o_d if tl_record else "Unknown"
            actual_d_o_d = tl_record.Actual_d_o_d if tl_record else "Unknown"

            exclude_remarks = [
                "Work to H", "Break to Hold", "Meeting to Hold", "Call to Hold", 
                "WL to H", "CL to H", "BL to H", "ML to H", "New hold record for tomorrow"
            ]

            # Fetch all hold records for the service_id
            hold_records = db.query(models.HOLD).filter(models.HOLD.Service_ID == service_id).all()

            # Concatenate the remarks, excluding the ones in the `exclude_remarks` list
            remarks = ", ".join([r.remarks for r in hold_records if r.remarks and r.remarks not in exclude_remarks]) if hold_records else None

            # Calculate number of days delayed
            if estimated_d_o_d != "Unknown" and actual_d_o_d != "Unknown":
                try:
                    estimated_date = datetime.strptime(estimated_d_o_d, "%Y-%m-%d")
                    actual_date = datetime.strptime(actual_d_o_d, "%Y-%m-%d")
                    days_delayed = (actual_date - estimated_date).days
                except ValueError:
                    days_delayed = "Invalid Date"
            else:
                days_delayed = "N/A"

            # Populate user_times dictionary
            user_times[username][service_id] = {
                'nature_of_work': nature_of_work.work_name if nature_of_work else "Unknown",  
                'entity': entity,
                'gst': gstintan,
                'estimated_d_o_d': estimated_d_o_d,
                'actual_d_o_d': actual_d_o_d,
                'adherence_of_delivery': actual_d_o_d,  # Assuming this is what you want
                'No.of.days.delayed': days_delayed,
                'Count': Count,
                "Remarks": remarks,
            }

        # Only add the summary if there was data for the day
        if user_times:
            for username, services in user_times.items():
                for service_id, details in services.items():
                    daily_summaries.append({
                        'username': username,
                        'service_id': service_id,
                        'date': current_day.strftime("%Y-%m-%d"),
                        'Name_of_entity': details['entity'],
                        'GSTIN/TAN': details['gst'],
                        'nature_of_work': details['nature_of_work'],
                        'estimated_d_o_d': details['estimated_d_o_d'],
                        'actual_d_o_d': details['actual_d_o_d'],
                        'adherence_of_delivery': details['adherence_of_delivery'],
                        'No.of.days.delayed': details['No.of.days.delayed'],
                        'Count': details['Count'],
                        "Remarks": details['Remarks'],
                    })

        current_day += timedelta(days=1)

    return daily_summaries
