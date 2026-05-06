import { useNavigate } from "react-router-dom";

export default function StaffCard({ member }) {
    const navigate = useNavigate()

    return (
        <div
            onClick={() => navigate(`/staff/${member.id}`)}
            className="bg-white rounded-xl p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow border border-gray-100"
        >
            <p className="font-medium text-gray-800 text-sm">{member.short_name}</p>
            <p className="text-xs text-gray-500 mt-1">
                {member.pending_count} pending
                {member.overdue_count > 0 && 
                <span className="text-red-500 ml-1">{member.overdue_count} overdue</span> 
                }
            </p>    
        </div>
    )
}