import { useNavigate } from "react-router-dom";

export default function StaffCard({ member }) {
    const navigate = useNavigate()

    return (
        <div
            onClick={() => navigate(`/staff/${member.id}`)}
            className=""
        >
            <p>{member.short_name}</p>
            <p>
                {member.pending_count} pending
                {member.overdue_count > 0 &&
                    `. ${member.overdue_count} overdue`
                }
            </p>    
        </div>
    )
}