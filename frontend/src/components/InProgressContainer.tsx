import { Message, MessageFragment } from '../Messages'
import { calculateSpinnerMessage } from '../utils'
import { Spinner } from './Spinner'
import { SystemMessageContainer } from './SystemMessageContainer'

type Props = {
  fragments: MessageFragment[]
  progress: number | null
  status: string
}

const statusMap = {
  "requested": "Generation requested...",
  "sceduled": "Staring response generation...",
  "started": "Generating response...",
  "completed": false
} as Record<string, string | false>


export default function InProgressContainer({progress, fragments, status}: Props) {
  const message : Message = {
    fragments,
    decision: [],
    senderRole: "system",
  }

  const resolvedStatus: string | false = statusMap[status] === undefined ? status : statusMap[status]

  return (
      <SystemMessageContainer message={message} hideDecision>
        {"..."}
        { progress != null &&
          <Spinner
            message={calculateSpinnerMessage(progress)}
          />
        }
        {resolvedStatus &&
          <div className="grid w-full justify-items-center text-gray-400 text-sm">
            {resolvedStatus}
          </div>
        }
      </SystemMessageContainer>
  )
}
