export default function Button({ children, type }) {
  return (
    <button
      type={type || 'submit'}
      className='rounded-full bg-blue-500 px-5 py-2 text-xl text-slate-50 hover:bg-blue-400'
    >
      {children}
    </button>
  )
}
