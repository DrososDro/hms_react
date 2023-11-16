import { Form } from 'react-router-dom'
import Button from '../components/Button'

export default function Login() {
  return (
    <div className='flex h-screen w-full items-center justify-center'>
      <div className='rounded-2xl border-2 border-slate-400 bg-slate-300 px-7 py-10  md:w-2/5'>
        <form>
          <h1 className='text-center text-3xl font-bold'>HMS Login</h1>
          <div className='mx-4 my-2 flex flex-col'>
            <label htmlFor='email' className='pl-5'>
              Email
            </label>
            <input
              name='email'
              id='email'
              type='text'
              className='rounded-full px-5 py-2 outline-none focus:ring focus:ring-slate-400'
            />
          </div>
          <div className='mx-4 my-2 flex flex-col'>
            <label htmlFor='password' className='pl-5'>
              Password
            </label>
            <input
              name='password'
              id='password'
              type='password'
              className='rounded-full px-5 py-2 outline-none focus:ring focus:ring-slate-400'
            />
          </div>
          <div className='px-5 py-2'>
            <Button>Login</Button>
          </div>
          <div className='flex justify-between px-5 pt-5'>
            <span>Don&#39;t have an account</span>
            <a href='#' className='text-blue-600 hover:text-blue-500'>
              Register
            </a>
          </div>
        </form>
      </div>
    </div>
  )
}
